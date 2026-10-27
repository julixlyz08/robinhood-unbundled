"""
Step 10: score the Q3 2026 forecast (made Oct 18, 2026) against Robinhood's reported results (Oct 27, 2026).

Every forecast line was activity x earnings per unit, so each miss is split into:
  - activity error: did we get the volume right?
  - pricing error: did Robinhood earn what we assumed per unit?

Run:  python src/score_q3.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
f = pd.read_csv(ROOT / "outputs/q3_2026_forecast.csv").set_index("vertical")
a = pd.read_csv(ROOT / "data/processed/quarters.csv").set_index("quarter").loc["2026Q3"]

actual = {
    "Options": a.options_rev, "Equities": a.equities_rev, "Crypto": a.crypto_rev,
    "Prediction markets": a.event_contracts_rev, "Subscriptions & Banking": a.other_rev,
    "Other transaction (not analyzed)": a.other_transaction_rev, "Net interest (not analyzed)": a.net_interest_rev,
    "TOTAL NET REVENUE": a.total_net_rev,
}
actual_volume = {"Options": a.options_contracts_m, "Equities": a.equity_notional_b,
                 "Crypto": a.crypto_notional_app_b, "Prediction markets": a.event_contracts_b,
                 "Subscriptions & Banking": a.gold_subs_m}
# what Robinhood actually earned per unit in Q3 (same units as the forecast's take rates)
actual_rate = {"Options": a.options_rev / a.options_contracts_m,
               "Equities": a.equities_rev / a.equity_notional_b * 10,
               "Crypto": (a.crypto_rev - a.crypto_notional_bitstamp_b * 0.053) / a.crypto_notional_app_b * 10,
               "Prediction markets": a.event_contracts_rev / a.event_contracts_b / 10}

rows = []
for v, act in actual.items():
    r = f.loc[v]
    row = {"line": v, "forecast": r.rev_base, "low": r.rev_low, "high": r.rev_high, "actual": act,
           "error_pct": (r.rev_base / act - 1) * 100,
           "within_range": "yes" if r.rev_low <= act <= r.rev_high else ("below" if act < r.rev_low else "above")}
    if v in actual_volume and pd.notna(r.get("q3_volume")):
        row["volume_forecast"] = r.q3_volume
        row["volume_actual"] = actual_volume[v]
        row["volume_error_pct"] = (r.q3_volume / actual_volume[v] - 1) * 100
    if v in actual_rate:
        row["rate_forecast"] = r.take_rate_base
        row["rate_actual"] = actual_rate[v]
        row["rate_error_pct"] = (r.take_rate_base / actual_rate[v] - 1) * 100
    rows.append(row)
s = pd.DataFrame(rows)
s.to_csv(ROOT / "outputs/q3_2026_scorecard.csv", index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(s.round(2).to_string(index=False))
