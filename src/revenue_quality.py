"""
Step 6: revenue quality. How much of each vertical's revenue moves with market mood?

For each vertical we fit, on quarterly data since the 2021 IPO:
    log(revenue) = a + b * time  +  c * log(VIX)  +  d * log(Bitcoin price)

and split the variation in revenue into:
    - steady growth   = R² of a time-trend-only model
    - market mood     = extra R² gained by adding VIX and Bitcoin
    - unexplained     = what neither explains (product launches, one-offs, noise)

Logs mean coefficients read as elasticities: d = 1.2 means a 10% higher Bitcoin price
goes with ~12% higher revenue.

Prediction markets are excluded: only one quarter of clean revenue so far.

Run:  python src/revenue_quality.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
q = pd.read_csv(ROOT / "data/processed/quarters.csv")
mkt = pd.read_csv(ROOT / "data/raw/market_conditions.csv")
df = q.merge(mkt, on="quarter", how="inner").reset_index(drop=True)
df["t"] = np.arange(len(df))
df["log_vix"] = np.log(df.vix_avg)
df["log_btc"] = np.log(df.btc_avg_usd)

LINES = {"Options": "options_rev", "Equities": "equities_rev", "Crypto": "crypto_rev",
         "Subscriptions & Banking": "other_rev", "Net interest (reference)": "net_interest_rev",
         "Total net revenue": "total_net_rev"}

rows = []
for name, col in LINES.items():
    d = df.dropna(subset=[col])
    y = np.log(d[col])
    trend = sm.OLS(y, sm.add_constant(d[["t"]])).fit()
    full = sm.OLS(y, sm.add_constant(d[["t", "log_vix", "log_btc"]])).fit()
    rows.append({
        "line": name, "quarters": len(d),
        "steady_growth_share": trend.rsquared,
        "market_mood_share": full.rsquared - trend.rsquared,
        "unexplained_share": 1 - full.rsquared,
        "growth_per_quarter": np.exp(full.params["t"]) - 1,   # trend growth holding market constant
        "vix_elasticity": full.params["log_vix"], "vix_pvalue": full.pvalues["log_vix"],
        "btc_elasticity": full.params["log_btc"], "btc_pvalue": full.pvalues["log_btc"],
    })
res = pd.DataFrame(rows)

# Stress test: what happens to each line's quarterly revenue if Bitcoin falls 30%
# (VIX held constant)? Uses the estimated elasticities on Q2 2026 revenue.
q2 = q.set_index("quarter").loc["2026Q2"]
res["q2_2026_revenue"] = [q2[c] for c in LINES.values()]
res["btc_minus30_change_pct"] = (0.7 ** res.btc_elasticity - 1) * 100
res["btc_minus30_change_m"] = res.q2_2026_revenue * res.btc_minus30_change_pct / 100
res.to_csv(ROOT / "outputs/revenue_quality.csv", index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(f"{len(df)} quarters: {df.quarter.iloc[0]} to {df.quarter.iloc[-1]}\n")
    print(res.round(2).to_string(index=False))
