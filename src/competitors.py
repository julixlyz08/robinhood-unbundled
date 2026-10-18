"""
Step 5: competitiveness. For each vertical, compare Robinhood with its most relevant
rivals on three things, using Q2 2026 vs Q2 2025 (the latest quarter everyone reported):

  1. Activity growth   - is Robinhood gaining or losing share of customer activity?
  2. Take rate         - does it earn more or less per unit than rivals?
  3. Scale             - how big is it relative to them?

Only like-for-like metrics are compared; where definitions differ, the row says so.

Run:  python src/competitors.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
q = pd.read_csv(ROOT / "data/processed/quarters.csv").set_index("quarter")
c = pd.read_csv(ROOT / "data/raw/competitors.csv")


def peer(company, metric_startswith, period):
    s = c[(c.company == company) & c.metric.str.startswith(metric_startswith) & (c.period == period)]
    return float(s.value.iloc[0]) if len(s) else float("nan")


def growth(new, old):
    return new / old - 1


h25, h26 = q.loc["2025Q2"], q.loc["2026Q2"]
rows = []
def add(vertical, measure, company, q2_26, q2_25=None, unit="", note=""):
    rows.append({"vertical": vertical, "measure": measure, "company": company, "q2_2026": q2_26,
                 "q2_2025": q2_25, "yoy_growth": growth(q2_26, q2_25) if q2_25 else None,
                 "unit": unit, "note": note})

# --- Options: contracts traded --------------------------------------------------------
add("Options", "contracts traded", "Robinhood", h26.options_contracts_m, h25.options_contracts_m, "M contracts")
add("Options", "contracts traded", "Interactive Brokers",
    peer("Interactive Brokers", "Customer options", "Q2 2026"),
    peer("Interactive Brokers", "Customer options", "Q2 2025"), "M contracts")
add("Options", "contracts traded", "Webull",
    peer("Webull", "Options contracts", "Q2 2026"), peer("Webull", "Options contracts", "Q2 2025"), "M contracts")

# --- Equities: notional traded / trades -----------------------------------------------
add("Equities", "equity notional traded", "Robinhood", h26.equity_notional_b, h25.equity_notional_b, "$B")
add("Equities", "equity notional traded", "Webull",
    peer("Webull", "Equity notional", "Q2 2026"), peer("Webull", "Equity notional", "Q2 2025"), "$B")
add("Equities", "daily average trades (all products)", "Charles Schwab",
    peer("Charles Schwab", "Clients' Daily", "Q2 2026"), peer("Charles Schwab", "Clients' Daily", "Q2 2025"), "M/day",
    "Schwab counts trades, not dollars; growth rate is the comparable part")
add("Equities", "daily average revenue trades (all products)", "Interactive Brokers",
    peer("Interactive Brokers", "Total Customer DARTs", "Q2 2026"),
    peer("Interactive Brokers", "Total Customer DARTs", "Q2 2025"), "M/day", "growth rate is the comparable part")

# --- Crypto: retail take rate and volume ----------------------------------------------
hood_app_bps = 54.9   # solved in src/forecast_q3.py from Q1+Q2 2026 (app vs Bitstamp split)
cb_rev = peer("Coinbase", "Consumer, net", "Q2 2026")
cb_vol = peer("Coinbase", "Consumer trading volume", "Q2 2026")
add("Crypto", "retail volume", "Robinhood (app)", h26.crypto_notional_app_b, h25.crypto_notional_app_b, "$B")
add("Crypto", "retail volume", "Coinbase (consumer)", cb_vol, peer("Coinbase", "Consumer trading volume", "Q2 2025"), "$B")
add("Crypto", "retail take rate", "Robinhood (app)", hood_app_bps, None, "bps", "estimated: app vs Bitstamp solved from two quarters")
add("Crypto", "retail take rate", "Coinbase (consumer)", cb_rev / cb_vol * 10, None, "bps", "consumer transaction revenue / consumer volume")
add("Crypto", "institutional volume", "Robinhood (Bitstamp)", h26.crypto_notional_bitstamp_b, None, "$B",
    "Q2 2025 had only one month of Bitstamp")
add("Crypto", "institutional volume", "Coinbase (institutional)", peer("Coinbase", "Institutional trading", "Q2 2026"),
    peer("Coinbase", "Institutional trading", "Q2 2025"), "$B")

# --- Prediction markets: annualized revenue and valuation of the venues ---------------
add("Prediction markets", "annualized revenue", "Robinhood", h26.event_contracts_rev * 4, None, "$M", "Q2 2026 x 4")
add("Prediction markets", "annualized revenue", "Coinbase", peer("Coinbase", "Annualized prediction", "Q2 2026"), None, "$M",
    "company says '$100M+'")
add("Prediction markets", "annualized revenue run-rate", "Kalshi", peer("Kalshi", "Annualized revenue", "Jul 2026"), None, "$M",
    "press reports, not a filing; Kalshi is the exchange many brokers (incl. Robinhood) route to")
add("Prediction markets", "annualized revenue", "Polymarket", peer("Polymarket", "Annualized revenue", "Jun 2026"), None, "$M",
    "press reports, lower bound")

# --- Subscriptions & Banking ----------------------------------------------------------
add("Subscriptions & Banking", "paying members / subscribers", "Robinhood (Gold)", h26.gold_subs_m, h25.gold_subs_m, "M")
add("Subscriptions & Banking", "members", "SoFi", peer("SoFi", "Members", "Q2 2026"), peer("SoFi", "Members", "Q2 2025"), "M",
    "SoFi members are all customers, not paying subscribers")
add("Subscriptions & Banking", "subscription & service revenue", "Robinhood (other revenues)", h26.other_rev, h25.other_rev, "$M")
add("Subscriptions & Banking", "financial services revenue", "SoFi",
    peer("SoFi", "Total net revenue - Financial", "Q2 2026"), peer("SoFi", "Total net revenue - Financial", "Q2 2025"), "$M")
add("Subscriptions & Banking", "subscription & services revenue", "Coinbase",
    peer("Coinbase", "Total subscription", "Q2 2026"), peer("Coinbase", "Total subscription", "Q2 2025"), "$M",
    "mostly interest on USDC and staking, so rate- and crypto-sensitive")

out = pd.DataFrame(rows)
out.to_csv(ROOT / "outputs/competitive_scorecard.csv", index=False)

# Share of activity among the brokers we can measure in the same unit
share = {}
for v, comp in [("Options", ["Robinhood", "Interactive Brokers", "Webull"]),
                ("Equities", ["Robinhood", "Webull"])]:
    sub = out[(out.vertical == v) & out.company.isin(comp) & ~out.measure.str.contains("daily")]
    for col in ["q2_2026", "q2_2025"]:
        share[(v, col)] = sub.set_index("company")[col]["Robinhood"] / sub[col].sum()

if __name__ == "__main__":
    pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 50)
    f = out.copy()
    f["yoy_growth"] = (f.yoy_growth * 100).round(0).astype("Int64").astype(str).str.replace("<NA>", "") + "%"
    print(f.drop(columns="note").round(1).to_string(index=False))
    print("\nRobinhood share of measured activity:")
    for (v, col), s in share.items():
        print(f"  {v:10s} {col}: {s:.0%}")
