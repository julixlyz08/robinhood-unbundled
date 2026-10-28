"""
Step 3: forecast Q3 2026 revenue per vertical BEFORE Robinhood reports (Oct 27, 2026).

Logic:  revenue = activity (volume) x take rate (revenue per unit of activity)
  - Activity for Jul + Aug comes from the monthly releases; September is only published
    for Sep 1-24, so it is scaled up to the full month.
  - Take rates come from the quarterly history (src/build_dataset.py).
  - Every vertical gets a low / base / high range, not a single number.

Before trusting it, the script backtests the same method on past quarters:
"if we had used last quarter's take rate x this quarter's actual volume, how close
would we have been?"

Run:  python src/forecast_q3.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
q = pd.read_csv(ROOT / "data/processed/quarters.csv")
t = pd.read_csv(ROOT / "data/processed/take_rates.csv")
m = pd.read_csv(ROOT / "data/raw/monthly_metrics.csv").set_index("month")
# The forecast was made on Oct 18, 2026 with data through Q2 2026; keep it that way on reruns.
q = q[q.quarter <= "2026Q2"]
t = t[t.quarter <= "2026Q2"]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# A. Q3 2026 activity
# ---------------------------------------------------------------------------
# September month-to-date release (Sep 1-24, published Sep 28, 2026)
sep_mtd = {"equity_notional_b": 267, "options_contracts_m": 234,
           "crypto_notional_app_b": 7, "crypto_notional_bitstamp_b": 10, "event_contracts_b": 4.4}

# Stocks/options trade on market days; crypto and prediction markets trade every day.
us_holidays_2026 = [np.datetime64("2026-09-07")]                     # Labor Day
td_mtd = np.busday_count("2026-09-01", "2026-09-25", holidays=us_holidays_2026)   # Sep 1-24
td_full = np.busday_count("2026-09-01", "2026-10-01", holidays=us_holidays_2026)  # all Sep
cal_mtd, cal_full = 24, 30

scale = {"equity_notional_b": td_full / td_mtd, "options_contracts_m": td_full / td_mtd,
         "crypto_notional_app_b": cal_full / cal_mtd, "crypto_notional_bitstamp_b": cal_full / cal_mtd,
         "event_contracts_b": cal_full / cal_mtd}
sep_full = {k: v * scale[k] for k, v in sep_mtd.items()}

vol = {k: m.loc["2026-07", k] + m.loc["2026-08", k] + sep_full[k] for k in sep_mtd}

# ---------------------------------------------------------------------------
# B. Take rates (low / base / high)
# ---------------------------------------------------------------------------
def backtest_mae(rate_col, vol_col, rev_col, scale=1.0):
    """How wrong has 'last quarter's take rate x this quarter's volume' been, on average?"""
    h = q.merge(t, on=["quarter", "period_end"]).dropna(subset=[rate_col])
    pred = h[vol_col] * h[rate_col].shift(1) * scale
    return ((pred / h[rev_col] - 1).abs()).dropna().mean()

def rng(col, mae):
    """base = latest quarter; low/high = base -/+ the method's average historical error."""
    base = t.dropna(subset=[col])[col].iloc[-1]
    return base * (1 - mae), base, base * (1 + mae)

opt_mae = backtest_mae("options_usd_per_contract", "options_contracts_m", "options_rev")
eq_mae = backtest_mae("equities_bps", "equity_notional_b", "equities_rev", scale=0.1)
opt_lo, opt_base, opt_hi = rng("options_usd_per_contract", opt_mae)
eq_lo, eq_base, eq_hi = rng("equities_bps", eq_mae)

# Crypto revenue covers two very different businesses: the retail app (high take rate)
# and Bitstamp (institutional, tiny take rate). Solve for both rates from the two most
# recent quarters, where volume is split:  rev = app_vol*a + bitstamp_vol*b
r1, r2 = q[q.quarter == "2026Q1"].iloc[0], q[q.quarter == "2026Q2"].iloc[0]
A = np.array([[r1.crypto_notional_app_b, r1.crypto_notional_bitstamp_b],
              [r2.crypto_notional_app_b, r2.crypto_notional_bitstamp_b]])
a, b = np.linalg.solve(A, [r1.crypto_rev, r2.crypto_rev])  # $M per $B of volume
crypto_app_bps, crypto_bitstamp_bps = a * 10, b * 10

# Prediction markets: only one quarter (Q2 2026) splits event-contract revenue out,
# so the range is wider (+/-15%). Rothera (own exchange, launched June 2026) could
# move this either way.
ev_base = t.loc[t.quarter == "2026Q2", "event_cents_per_contract"].iloc[0]

# ---------------------------------------------------------------------------
# C. Forecast
# ---------------------------------------------------------------------------
rows = []
def add(vertical, driver, volume, unit, lo, base, hi, to_rev):
    rows.append({"vertical": vertical, "driver": driver, "q3_volume": round(volume, 1), "unit": unit,
                 "take_rate_low": round(lo, 3), "take_rate_base": round(base, 3), "take_rate_high": round(hi, 3),
                 "rev_low": round(to_rev(volume, lo)), "rev_base": round(to_rev(volume, base)),
                 "rev_high": round(to_rev(volume, hi))})

add("Options", "options contracts (M)", vol["options_contracts_m"], "$/contract",
    opt_lo, opt_base, opt_hi, lambda v, r: v * r)
add("Equities", "equity notional ($B)", vol["equity_notional_b"], "bps",
    eq_lo, eq_base, eq_hi, lambda v, r: v * r / 10)
app_v, bs_v = vol["crypto_notional_app_b"], vol["crypto_notional_bitstamp_b"]
bs_rev = bs_v * crypto_bitstamp_bps / 10
add("Crypto", "app crypto notional ($B) (+ Bitstamp)", app_v, "app bps",
    crypto_app_bps * 0.9, crypto_app_bps, crypto_app_bps * 1.1, lambda v, r: v * r / 10 + bs_rev)
add("Prediction markets", "event contracts (B)", vol["event_contracts_b"], "cents/contract",
    ev_base * 0.85, ev_base, ev_base * 1.15, lambda v, r: v * r * 10)

# Subscriptions & Banking ("other revenues"): no monthly Gold data, so grow Q2 by the
# recent pace of Gold additions (+0.5M/quarter -> ~5.3M). Trump Accounts launched July 4,
# which adds real uncertainty in both directions.
other_q2 = q.loc[q.quarter == "2026Q2", "other_rev"].iloc[0]
gold_growth = 5.3 / 4.8
rows.append({"vertical": "Subscriptions & Banking", "driver": "Gold subscribers (M, est.)",
             "q3_volume": 5.3, "unit": "", "take_rate_low": np.nan, "take_rate_base": np.nan,
             "take_rate_high": np.nan, "rev_low": round(other_q2), "rev_base": round(other_q2 * gold_growth),
             "rev_high": round(other_q2 * gold_growth * 1.08)})

f = pd.DataFrame(rows)

# Not-analyzed lines, held near Q2 so the total is comparable to reported revenue
other_trans = q.loc[q.quarter == "2026Q2", "other_transaction_rev"].iloc[0]
nii = q.loc[q.quarter == "2026Q2", "net_interest_rev"].iloc[0]
for name, base in [("Other transaction (not analyzed)", other_trans), ("Net interest (not analyzed)", nii)]:
    f.loc[len(f)] = {"vertical": name, "rev_low": round(base * 0.95), "rev_base": round(base),
                     "rev_high": round(base * 1.05)}
f.loc[len(f)] = {"vertical": "TOTAL NET REVENUE", "rev_low": f.rev_low.sum(),
                 "rev_base": f.rev_base.sum(), "rev_high": f.rev_high.sum()}
f.to_csv(OUT / "q3_2026_forecast.csv", index=False)

# ---------------------------------------------------------------------------
# D. Backtest: last quarter's take rate x this quarter's actual volume
# ---------------------------------------------------------------------------
bt = []
hist = q.merge(t, on=["quarter", "period_end"]).dropna(subset=["options_usd_per_contract"]).reset_index(drop=True)
for i in range(1, len(hist)):
    prev, cur = hist.iloc[i - 1], hist.iloc[i]
    bt.append({"quarter": cur.quarter,
               "options_err_pct": (cur.options_contracts_m * prev.options_usd_per_contract / cur.options_rev - 1) * 100,
               "equities_err_pct": (cur.equity_notional_b * prev.equities_bps / 10 / cur.equities_rev - 1) * 100})
bt = pd.DataFrame(bt)
bt.to_csv(OUT / "forecast_backtest.csv", index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(f"September trading days: {td_mtd} of {td_full} in the Sep 1-24 release\n")
    print("Q3 2026 activity:", {k: round(v, 1) for k, v in vol.items()}, "\n")
    print(f"Crypto take rates solved from Q1+Q2 2026: app {crypto_app_bps:.1f} bps, Bitstamp {crypto_bitstamp_bps:.2f} bps\n")
    print(f.to_string(index=False))
    print("\nBacktest (positive = method would have overestimated):")
    print(bt.round(1).to_string(index=False))
    print(f"\nMean absolute error: options {bt.options_err_pct.abs().mean():.1f}%, "
          f"equities {bt.equities_err_pct.abs().mean():.1f}%")
