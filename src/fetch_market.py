"""
Fetch the market data used in Steps 6-7, so it never has to be collected by hand.

  - VIX (market fear gauge) and Bitcoin price, daily, from FRED (free, no key needed)
    -> averaged per quarter -> data/raw/market_conditions_fred.csv
  - Share price, market cap and revenue multiples for Robinhood and its peers, from Yahoo
    Finance via the yfinance package -> data/raw/valuation_snapshot.csv

Run:  python src/fetch_market.py
"""
from datetime import date
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def fred(series):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    text = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
    df = pd.read_csv(StringIO(text))
    df.columns = ["date", series]
    df["date"] = pd.to_datetime(df["date"])
    df[series] = pd.to_numeric(df[series], errors="coerce")   # FRED marks missing days with "."
    return df.dropna().set_index("date")[series]


def market_conditions():
    vix, btc = fred("VIXCLS"), fred("CBBTCUSD")
    q = pd.DataFrame({"vix_avg": vix.resample("QE").mean(), "btc_avg_usd": btc.resample("QE").mean()})
    q = q.loc["2021-04-01":]
    q.index = q.index.to_period("Q").astype(str)   # e.g. 2021Q2
    q.index.name = "quarter"
    q.round(2).to_csv(RAW / "market_conditions_fred.csv")
    return q


def valuation_snapshot():
    import yfinance as yf
    rows = []
    for ticker in ["HOOD", "IBKR", "SCHW", "COIN", "SOFI", "CME", "ICE", "CBOE"]:
        info = yf.Ticker(ticker).info
        rows.append({
            "ticker": ticker, "date": date.today().isoformat(),
            "share_price": info.get("currentPrice"),
            "market_cap_b": (info.get("marketCap") or 0) / 1e9,
            "enterprise_value_b": (info.get("enterpriseValue") or 0) / 1e9,
            "ttm_revenue_m": (info.get("totalRevenue") or 0) / 1e6,
            "ttm_ebitda_m": (info.get("ebitda") or 0) / 1e6,
            "forward_pe": info.get("forwardPE"),
            "ev_to_ttm_revenue": info.get("enterpriseToRevenue"),
        })
    df = pd.DataFrame(rows)
    df.round(2).to_csv(RAW / "valuation_snapshot.csv", index=False)
    return df


if __name__ == "__main__":
    print(market_conditions().round(1).to_string())
    try:
        print(valuation_snapshot().round(1).to_string(index=False))
    except Exception as e:   # Yahoo occasionally rate-limits; market conditions are the critical part
        print("Valuation snapshot failed:", e)
