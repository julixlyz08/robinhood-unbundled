"""
Step 1 + 2: merge the raw quarterly files into one clean table, check it adds up,
then compute each vertical's take rate (revenue earned per unit of activity).

Run:  python src/build_dataset.py
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Merge every quarterly file collected from the earnings releases
# ---------------------------------------------------------------------------
files = sorted(RAW.glob("quarter*.csv"))
q = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
q = q.drop_duplicates("quarter", keep="last").sort_values("period_end").reset_index(drop=True)

# Provision for credit losses is mostly the Gold Card. It is recorded in the notes
# column (the releases list it as its own expense line), so pull it out into a column.
def provision(note):
    m = re.search(r"[Pp]rovision for credit losses\D{0,20}?(\d+)", str(note))
    return float(m.group(1)) if m else 0.0

# In older releases the provision is buried inside other expense lines (it shows up
# only in the cash-flow statement), so it must NOT be counted again. Treat it as its
# own line only when the five main lines fall short of the total by that amount.
five = ["brokerage_transaction_exp", "tech_dev_exp", "operations_exp", "marketing_exp", "g_and_a_exp"]
gap = q["total_opex"] - q[five].fillna(0).sum(axis=1)
prov = q["notes"].apply(provision)
q["credit_loss_exp"] = prov.where((gap - prov).abs() <= 2, 0.0)

# ---------------------------------------------------------------------------
# 2. Checks: do the pieces add up to the reported totals?
# ---------------------------------------------------------------------------
parts = ["options_rev", "crypto_rev", "equities_rev", "event_contracts_rev", "other_transaction_rev"]
# Before 2025 Robinhood didn't print an "other transaction" line; the gap between the
# named products and the transaction total IS that line, so fill it in and flag it.
named = q[parts[:4]].fillna(0).sum(axis=1)
missing_other = q["other_transaction_rev"].isna()
q["other_transaction_derived"] = missing_other
q.loc[missing_other, "other_transaction_rev"] = (q["transaction_rev_total"] - named)[missing_other].round(1)

q["chk_transaction"] = q[parts].fillna(0).sum(axis=1) - q["transaction_rev_total"]
q["chk_total_rev"] = q[["transaction_rev_total", "net_interest_rev", "other_rev"]].sum(axis=1) - q["total_net_rev"]
q["unexplained_opex"] = gap - q["credit_loss_exp"]

q.to_csv(OUT / "quarters.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Take rates: what Robinhood earns per unit of customer activity
# ---------------------------------------------------------------------------
t = q[["quarter", "period_end"]].copy()

# Options: dollars per contract traded
t["options_usd_per_contract"] = q["options_rev"] / q["options_contracts_m"]

# Equities: basis points of notional traded (1 bp = 0.01%)
#   revenue $M / (notional $B * 1000) * 10,000  ==  revenue / notional * 10
t["equities_bps"] = q["equities_rev"] / q["equity_notional_b"] * 10

# Crypto: bps on all volume, and bps on retail app volume only.
# Bitstamp is institutional and earns far less per dollar, so the blended number
# drifts down as Bitstamp grows even if retail pricing is unchanged.
crypto_total = q["crypto_notional_app_b"] + q["crypto_notional_bitstamp_b"].fillna(0)
t["crypto_bps_blended"] = q["crypto_rev"] / crypto_total * 10
t["crypto_bps_app_only"] = q["crypto_rev"] / q["crypto_notional_app_b"] * 10

# Prediction markets: cents per event contract
#   revenue $M / contracts B  =  $ per 1,000 contracts  ->  /10 gives cents per contract
t["event_cents_per_contract"] = q["event_contracts_rev"] / q["event_contracts_b"] / 10

# Subscriptions & Banking: annualized other revenue per Gold subscriber ($)
t["other_rev_per_gold_sub_usd"] = q["other_rev"] * 4 / q["gold_subs_m"]

t.to_csv(OUT / "take_rates.csv", index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(f"{len(q)} quarters: {q['quarter'].iloc[0]} to {q['quarter'].iloc[-1]}\n")
    issues = q[(q["chk_transaction"].abs() > 1) | (q["chk_total_rev"].abs() > 1) | (q["unexplained_opex"].abs() > 2)]
    print("Rows that don't add up:" if len(issues) else "All rows reconcile to reported totals.")
    if len(issues):
        print(issues[["quarter", "chk_transaction", "chk_total_rev", "unexplained_opex"]].to_string(index=False))
    print("\nTake rates:")
    print(t.round(3).to_string(index=False))
