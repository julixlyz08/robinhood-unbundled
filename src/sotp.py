"""
Step 7: sum-of-the-parts (SOTP) valuation.

Idea: value each vertical as if it were a standalone company, using what the stock market
pays for its closest listed peers (enterprise value / next-year revenue), add them up,
add net cash, and compare with what Robinhood actually trades at.

Inputs
  - Next-year (FY2027) revenue per vertical: our Q3 2026 forecast mix, scaled so the total
    matches the analyst consensus for FY2027 ($6.85B). So we use the consensus for the size
    of the pie and our own work for how it is sliced.
  - Peer multiples (Oct 16, 2026 close) in data/raw/valuation_inputs.csv
  - Net cash: $3.16B (cash minus the 2029 convertible notes)

Outputs: low / base / high value per vertical, total vs market cap, and the
"market-implied" multiple on prediction markets (the most debated vertical).

Run:  python src/sotp.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
v = pd.read_csv(ROOT / "data/raw/valuation_inputs.csv").set_index("ticker")
f = pd.read_csv(ROOT / "outputs/q3_2026_forecast.csv").set_index("vertical")

HOOD_MCAP = v.loc["HOOD", "market_cap_b"]
NET_CASH = 3.16
SHARES_B = 0.912                         # diluted, Q2 2026
FY27_CONSENSUS = v.loc["HOOD", "forward_revenue_m"] / 1000

m = lambda t: v.loc[t, "ev_to_forward_revenue"]
ibkr = v.loc["IBKR", "market_cap_b"] / v.loc["IBKR", "forward_revenue_m"] * 1000   # IBKR has no meaningful EV
kalshi_rr = v.loc["private", "market_cap_b"].iloc[0] / 4.0                            # $22B / ~$4B run-rate
exchanges = (m("CME") + m("ICE") + m("CBOE")) / 3

# (low, base, high) EV / forward revenue, and which peers justify them
MULTIPLES = {
    "Options":                 ((m("SCHW"), (m("SCHW") + ibkr) / 2, ibkr), "Schwab - IBKR"),
    "Equities":                ((m("SCHW"), (m("SCHW") + ibkr) / 2, ibkr), "Schwab - IBKR"),
    "Crypto":                  ((m("COIN") * 0.8, m("COIN"), m("COIN") * 1.2), "Coinbase +/-20%"),
    "Prediction markets":      ((kalshi_rr, exchanges, m("CME")), "Kalshi last round - exchange avg - CME"),
    "Subscriptions & Banking": ((m("SOFI"), (m("SOFI") + 8) / 2, 8.0), "SoFi - subscription premium (judgment)"),
    "Other transaction (not analyzed)": ((m("SCHW"), (m("SCHW") + ibkr) / 2, ibkr), "Schwab - IBKR"),
    "Net interest (not analyzed)":      ((m("SOFI"), m("SCHW"), 6.0), "SoFi - Schwab - judgment"),
}

parts = f.drop(index="TOTAL NET REVENUE").rev_base
fy27 = parts / parts.sum() * FY27_CONSENSUS                                  # $B

rows = []
for line, ((lo, base, hi), peers) in MULTIPLES.items():
    rev = fy27[line]
    rows.append({"line": line, "fy27_revenue_b": rev, "peers": peers,
                 "multiple_low": lo, "multiple_base": base, "multiple_high": hi,
                 "value_low_b": rev * lo, "value_base_b": rev * base, "value_high_b": rev * hi})
s = pd.DataFrame(rows)
s["share_of_value_base"] = s.value_base_b / s.value_base_b.sum()
s.to_csv(ROOT / "outputs/sotp.csv", index=False)

total = {k: s[f"value_{k}_b"].sum() + NET_CASH for k in ["low", "base", "high"]}

# What multiple on prediction markets would make the parts add up to today's market cap,
# holding everything else at base?
pm = s.set_index("line").loc["Prediction markets"]
others_base = s.value_base_b.sum() - pm.value_base_b
implied_pm_multiple = (HOOD_MCAP - NET_CASH - others_base) / pm.fy27_revenue_b

# Cross-check: price relative to growth. Revenue growth from trailing 12 months to FY2027
# consensus (same ~1.5-year span for every company), and the multiple paid per point of it.
g = v.drop(index="private").copy()
g["ev_or_mcap_b"] = g.enterprise_value_b.fillna(g.market_cap_b)
g["fwd_multiple"] = g.ev_or_mcap_b / g.forward_revenue_m * 1000
g["rev_growth_to_fy27"] = g.forward_revenue_m / g.ttm_revenue_m - 1
g["multiple_per_growth_pt"] = g.fwd_multiple / (g.rev_growth_to_fy27 * 100)
g = g.drop(index="CBOE")    # its trailing revenue is gross, consensus is net: growth not comparable
g[["company", "fwd_multiple", "rev_growth_to_fy27", "multiple_per_growth_pt"]].to_csv(ROOT / "outputs/growth_adjusted_multiples.csv")

if __name__ == "__main__":
    print(g[["company", "fwd_multiple", "rev_growth_to_fy27", "multiple_per_growth_pt"]].round(2).to_string(), "\n")
    pd.set_option("display.width", 220)
    print(s.round(2).to_string(index=False))
    print(f"\nSum of parts + net cash: low ${total['low']:.0f}B | base ${total['base']:.0f}B | high ${total['high']:.0f}B")
    print(f"Per share:               low ${total['low']/SHARES_B:.0f} | base ${total['base']/SHARES_B:.0f} | high ${total['high']/SHARES_B:.0f}")
    print(f"Market cap (Oct 16):     ${HOOD_MCAP:.1f}B  (${v.loc['HOOD','share_price']:.2f}/share)")
    print(f"\nMarket-implied prediction-markets multiple (others at base): {implied_pm_multiple:.1f}x "
          f"vs base {pm.multiple_base:.1f}x -> implied value ${implied_pm_multiple*pm.fy27_revenue_b:.0f}B")
