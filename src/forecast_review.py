"""
Step 10b: why the Q3 2026 forecast missed, and how it compares with the Zacks consensus.

1. Forecast vs Zacks consensus vs reported, line by line.
2. Each miss split into "activity" and "earnings per unit" (done in score_q3.py).
3. Two fixes tested after the fact, with the information that was available on Oct 18:
   - Net interest: grow it with the margin book (average of monthly balances) instead of holding it flat
   - Subscriptions & Banking: hold it flat (Q2's jump was Trump Account service revenue, not
     Gold growth) instead of growing it with Gold subscribers

Zacks consensus: Zacks Equity Research, published Oct 22, 2026 (total "$1.42 billion").
Its event-contracts estimate is not printed; it is implied as transaction-based revenue
minus the four named lines.

Run:  python src/forecast_review.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sc = pd.read_csv(ROOT / "outputs/q3_2026_scorecard.csv").set_index("line")
q = pd.read_csv(ROOT / "data/processed/quarters.csv").set_index("quarter")
m = pd.read_csv(ROOT / "data/raw/monthly_metrics.csv").set_index("month")

# Zacks consensus as published Oct 22, 2026 ("What Analyst Projections for Key Metrics Reveal
# About Robinhood Markets (HOOD) Q3 Earnings"). Headline total "$1.42 billion"; the total used
# here is the sum of its three revenue categories so every line is consistent.
zacks_trans = 847.75
zacks = {"Options": 364.11, "Equities": 120.34, "Crypto": 135.64, "Other transaction (not analyzed)": 45.79,
         "Net interest (not analyzed)": 441.02, "Subscriptions & Banking": 128.79}
zacks["Prediction markets"] = zacks_trans - 364.11 - 120.34 - 135.64 - 45.79   # implied, not printed
zacks["TOTAL NET REVENUE"] = zacks_trans + 441.02 + 128.79

order = ["Options", "Equities", "Crypto", "Prediction markets", "Subscriptions & Banking",
         "Other transaction (not analyzed)", "Net interest (not analyzed)", "TOTAL NET REVENUE"]
rows = []
for line in order:
    act = sc.loc[line, "actual"]
    mine = sc.loc[line, "forecast"]
    z = zacks[line]
    rows.append({"line": line, "my_forecast": mine, "zacks_consensus": round(z, 1), "reported": act,
                 "my_error_m": mine - act, "zacks_error_m": round(z - act, 1),
                 "my_error_pct": (mine / act - 1) * 100, "zacks_error_pct": (z / act - 1) * 100,
                 "closer": "tie" if abs(abs(mine - act) - abs(z - act)) < 0.5 else ("me" if abs(mine - act) < abs(z - act) else "Zacks")})
r = pd.DataFrame(rows)
r.to_csv(ROOT / "outputs/q3_2026_vs_zacks.csv", index=False)

lines_only = r[r.line != "TOTAL NET REVENUE"]
mine_abs = lines_only.my_error_m.abs().sum()
zacks_abs = lines_only.zacks_error_m.abs().sum()

# --- fixes tested after the fact ---------------------------------------------------------
# Net interest grown with the average margin book (Apr-Jun vs Jul-Aug, the months known on Oct 18)
mb_q2 = m.loc[["2026-04", "2026-05", "2026-06"], "margin_book_b"].mean()
mb_q3_known = m.loc[["2026-07", "2026-08"], "margin_book_b"].mean()
nii_fixed = q.loc["2026Q2", "net_interest_rev"] * mb_q3_known / mb_q2
subs_fixed = q.loc["2026Q2", "other_rev"]
total_fixed = (sc.loc["TOTAL NET REVENUE", "forecast"] - sc.loc["Net interest (not analyzed)", "forecast"] + nii_fixed
               - sc.loc["Subscriptions & Banking", "forecast"] + subs_fixed)
fixes = pd.DataFrame([
    {"line": "Net interest", "original": sc.loc["Net interest (not analyzed)", "forecast"], "fixed": nii_fixed,
     "reported": sc.loc["Net interest (not analyzed)", "actual"], "fix": "grow with margin book (+%.0f%%)" % ((mb_q3_known / mb_q2 - 1) * 100)},
    {"line": "Subscriptions & Banking", "original": sc.loc["Subscriptions & Banking", "forecast"], "fixed": subs_fixed,
     "reported": sc.loc["Subscriptions & Banking", "actual"], "fix": "hold flat at Q2"},
    {"line": "TOTAL NET REVENUE", "original": sc.loc["TOTAL NET REVENUE", "forecast"], "fixed": total_fixed,
     "reported": sc.loc["TOTAL NET REVENUE", "actual"], "fix": "both fixes"},
])
fixes.to_csv(ROOT / "outputs/q3_2026_fixes_tested.csv", index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(r.round(1).to_string(index=False))
    print(f"\nSum of absolute line errors: mine ${mine_abs:.0f}M, Zacks ${zacks_abs:.0f}M")
    print(f"Lines where I was closer: {(lines_only.closer == 'me').sum()} of {len(lines_only)}\n")
    print(fixes.round(1).to_string(index=False))
