"""
Step 9 prep: reshape the analysis into Tableau-friendly files (one row per thing, no
calculations left for Tableau except the interactive ones).

Outputs (tableau/):
  vertical_quarterly.csv  one row per quarter x vertical: revenue, volume, take rate,
                          plus Q3 2026 forecast rows (is_forecast = 1, with low/high)
  scorecard.csv           one row per vertical: the five questions in numbers
  sotp.csv                one row per line: valuation low/base/high, plus market cap row

Run:  python src/build_tableau.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tableau"
OUT.mkdir(exist_ok=True)

q = pd.read_csv(ROOT / "data/processed/quarters.csv")
t = pd.read_csv(ROOT / "data/processed/take_rates.csv")
f = pd.read_csv(ROOT / "outputs/q3_2026_forecast.csv").set_index("vertical")
pnl = pd.read_csv(ROOT / "data/processed/vertical_pnl_summary_2026q2.csv").set_index("line")
rq = pd.read_csv(ROOT / "outputs/revenue_quality.csv").set_index("line")
sotp = pd.read_csv(ROOT / "outputs/sotp.csv").set_index("line")
comp = pd.read_csv(ROOT / "outputs/competitive_scorecard.csv")
val = pd.read_csv(ROOT / "data/raw/valuation_inputs.csv").set_index("ticker")

# ---------------------------------------------------------------------------
# 1. Quarterly, long format
# ---------------------------------------------------------------------------
SPEC = {  # vertical: (revenue col, volume col, volume unit, take-rate col, take-rate unit)
    "Options": ("options_rev", "options_contracts_m", "M contracts", "options_usd_per_contract", "$ per contract"),
    "Equities": ("equities_rev", "equity_notional_b", "$B notional", "equities_bps", "bps"),
    "Crypto": ("crypto_rev", "crypto_notional_app_b", "$B notional (app)", "crypto_bps_app_only", "bps (app)"),
    "Prediction markets": ("event_contracts_rev", "event_contracts_b", "B contracts", "event_cents_per_contract", "cents per contract"),
    "Subscriptions & Banking": ("other_rev", "gold_subs_m", "M Gold subscribers", "other_rev_per_gold_sub_usd", "$ per Gold sub / yr"),
    "Other transaction": ("other_transaction_rev", None, "", None, ""),
    "Net interest": ("net_interest_rev", None, "", None, ""),
}
ANALYZED = ["Options", "Equities", "Crypto", "Prediction markets", "Subscriptions & Banking"]
qt = q.merge(t, on=["quarter", "period_end"])
rows = []
for _, r in qt.iterrows():
    for v, (rev, vol, vu, tr, tu) in SPEC.items():
        if pd.isna(r[rev]):
            continue
        rows.append({"quarter": r.quarter, "quarter_end": r.period_end, "vertical": v,
                     "analyzed": int(v in ANALYZED), "is_forecast": 0,
                     "revenue_m": r[rev], "revenue_low_m": None, "revenue_high_m": None,
                     "volume": r[vol] if vol else None, "volume_unit": vu,
                     "take_rate": r[tr] if tr else None, "take_rate_unit": tu,
                     "note": "includes prediction markets (not broken out before Q2 2026)"
                     if v == "Other transaction" and r.quarter in ("2025Q4", "2026Q1") else ""})
for v in ANALYZED + ["Other transaction (not analyzed)", "Net interest (not analyzed)"]:
    fr = f.loc[v]
    name = v.replace(" (not analyzed)", "")
    rows.append({"quarter": "2026Q3", "quarter_end": "2026-09-30", "vertical": name,
                 "analyzed": int(name in ANALYZED), "is_forecast": 1,
                 "revenue_m": fr.rev_base, "revenue_low_m": fr.rev_low, "revenue_high_m": fr.rev_high,
                 "volume": fr.get("q3_volume"), "volume_unit": SPEC[name][2],
                 "take_rate": fr.get("take_rate_base"), "take_rate_unit": SPEC[name][4],
                 "note": "forecast made 2026-10-18"})
vq = pd.DataFrame(rows)
vq.to_csv(OUT / "vertical_quarterly.csv", index=False)

# ---------------------------------------------------------------------------
# 2. Scorecard, one row per vertical
# ---------------------------------------------------------------------------
q25, q26 = q.set_index("quarter").loc["2025Q2"], q.set_index("quarter").loc["2026Q2"]
yoy = {"Options": q26.options_rev / q25.options_rev - 1, "Equities": q26.equities_rev / q25.equities_rev - 1,
       "Crypto": q26.crypto_rev / q25.crypto_rev - 1, "Prediction markets": None,   # not broken out in Q2 2025
       "Subscriptions & Banking": q26.other_rev / q25.other_rev - 1}
vol_yoy = {"Options": q26.options_contracts_m / q25.options_contracts_m - 1,
           "Equities": q26.equity_notional_b / q25.equity_notional_b - 1,
           "Crypto": q26.crypto_notional_app_b / q25.crypto_notional_app_b - 1,
           "Prediction markets": None, "Subscriptions & Banking": q26.gold_subs_m / q25.gold_subs_m - 1}
competitive = {"Options": "Gaining share (50% to 54% of contracts vs IBKR + Webull)",
               "Equities": "Gaining share (notional +85% vs Webull +73%)",
               "Crypto": "Holding share; ~1/3 of Coinbase's retail take rate",
               "Prediction markets": "Leading broker distributor (~6x Coinbase); exchanges keep most economics",
               "Subscriptions & Banking": "Revenue growing faster than SoFi (+54% vs +29%)"}
sc = []
for i, v in enumerate(ANALYZED, 1):
    sc.append({"sort": i, "vertical": v,
               "q2_2026_revenue_m": pnl.loc[v, "revenue"],
               "revenue_yoy": yoy[v], "volume_yoy": vol_yoy[v],
               "q3_2026_forecast_m": f.loc[v, "rev_base"],
               "contribution_margin": pnl.loc[v, "contribution_margin"],
               "operating_margin": pnl.loc[v, "operating_margin"],
               "operating_margin_min": pnl.loc[v, "min"], "operating_margin_max": pnl.loc[v, "max"],
               "operating_profit_m": pnl.loc[v, "operating_profit"],
               "market_mood_share": rq.loc[v, "market_mood_share"] if v in rq.index else None,
               "steady_growth_share": rq.loc[v, "steady_growth_share"] if v in rq.index else None,
               "btc_elasticity": rq.loc[v, "btc_elasticity"] if v in rq.index else None,
               "sotp_value_base_b": sotp.loc[v, "value_base_b"],
               "sotp_value_low_b": sotp.loc[v, "value_low_b"], "sotp_value_high_b": sotp.loc[v, "value_high_b"],
               "competitive_position": competitive[v]})
pd.DataFrame(sc).to_csv(OUT / "scorecard.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Valuation bridge
# ---------------------------------------------------------------------------
sv = sotp.reset_index()[["line", "fy27_revenue_b", "peers", "multiple_low", "multiple_base", "multiple_high",
                         "value_low_b", "value_base_b", "value_high_b"]]
sv["kind"] = "Vertical"
sv.loc[sv.line.str.contains("not analyzed"), "kind"] = "Not analyzed"
extra = pd.DataFrame([
    {"line": "Net cash", "kind": "Net cash", "value_low_b": 3.16, "value_base_b": 3.16, "value_high_b": 3.16},
    {"line": "Market cap (Oct 16, 2026)", "kind": "Market", "value_low_b": val.loc["HOOD", "market_cap_b"],
     "value_base_b": val.loc["HOOD", "market_cap_b"], "value_high_b": val.loc["HOOD", "market_cap_b"]},
])
sv = pd.concat([sv, extra], ignore_index=True)
sv.insert(0, "sort", range(1, len(sv) + 1))
sv.to_csv(OUT / "sotp.csv", index=False)

if __name__ == "__main__":
    print(f"vertical_quarterly.csv: {len(vq)} rows | scorecard.csv: {len(sc)} rows | sotp.csv: {len(sv)} rows")
    print(pd.read_csv(OUT / "scorecard.csv").iloc[:, :9].round(3).to_string(index=False))
