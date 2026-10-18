"""
Fetch the market data used in Steps 6-7, so it never has to be collected by hand.

  - VIX (market fear gauge) and Bitcoin price, daily, from Yahoo Finance
    (falls back to FRED, which is free but often slow)
    -> averaged per quarter -> data/raw/market_conditions_fred.csv
  - Share price, market cap and revenue multiples for Robinhood and its peers, from Yahoo
    Finance via the yfinance package -> data/raw/valuation_snapshot.csv

Run:  python src/fetch_market.py
"""
import time
from datetime import date
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


START = "2021-04-01"


def yahoo(ticker):
    """Daily closing prices from Yahoo Finance (fast, usually reliable)."""
    import yfinance as yf
    s = yf.download(ticker, start=START, progress=False, auto_adjust=False)["Close"]
    s = s.squeeze()                      # newer yfinance returns a one-column frame
    if s.empty:
        raise ValueError(f"no data for {ticker}")
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return s


def fred(series, tries=3):
    """Fallback: FRED CSV, only from 2021 on (smaller file), with retries."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={START}"
    for attempt in range(1, tries + 1):
        try:
            text = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=180).read().decode()
            break
        except Exception as e:
            print(f"  FRED {series} attempt {attempt} failed: {e}")
            if attempt == tries:
                raise
            time.sleep(5 * attempt)
    df = pd.read_csv(StringIO(text))
    df.columns = ["date", series]
    df["date"] = pd.to_datetime(df["date"])
    df[series] = pd.to_numeric(df[series], errors="coerce")   # FRED marks missing days with "."
    return df.dropna().set_index("date")[series]


def get(yahoo_ticker, fred_series):
    try:
        s = yahoo(yahoo_ticker)
        print(f"  {yahoo_ticker}: {len(s)} days from Yahoo Finance")
        return s
    except Exception as e:
        print(f"  Yahoo {yahoo_ticker} failed ({e}); trying FRED {fred_series}")
        return fred(fred_series)


def market_conditions():
    vix, btc = get("^VIX", "VIXCLS"), get("BTC-USD", "CBBTCUSD")
    q = pd.DataFrame({"vix_avg": vix.resample("QE").mean(), "btc_avg_usd": btc.resample("QE").mean()})
    q = q.loc[START:]
    q = q[q.index < pd.Timestamp.today().to_period("Q").start_time]   # drop the unfinished quarter
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
            "market_cap_b": (info.get("marketCap") or float("nan")) / 1e9,
            "enterprise_value_b": (info.get("enterpriseValue") or float("nan")) / 1e9,
            "ttm_revenue_m": (info.get("totalRevenue") or float("nan")) / 1e6,
            "ttm_ebitda_m": (info.get("ebitda") or float("nan")) / 1e6,
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
