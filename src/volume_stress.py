"""
Step 6b: trading-volume stress test. What happens to revenue and profit if customers trade less?

Logic (Q2 2026 as the base quarter):
  - Revenue of each trading line = volume x take rate. Volume falls by the scenario %;
    the take rate is held at its Q2 2026 level (see the equities cushion below).
  - Lines that do not depend on trading volume (Subscriptions & Banking, net interest) are
    held constant. That is generous: Gold revenue fell during the 2022 downturn, and the
    margin book shrinks when trading slows.
  - Costs: brokerage & transaction costs move with transaction revenue (they are ~8% of it);
    every other cost line is treated as fixed in the short run. So lost revenue falls almost
    entirely to the bottom line: operating leverage in reverse.

Scenarios
  - Uniform volume drops of 10%, 20%, 30%, 50% across all trading lines
  - "2022 replay": each line falls by its own 2021Q4-to-trough revenue drop
    (options -31%, equities -60%, crypto -52%); prediction markets and other transaction,
    which did not exist then, are assumed to fall like options (-31%).

Equities cushion: across 2024-2026, equities take rate moved against volume (correlation
-0.69): when volume falls, Robinhood earns more bps per dollar. A variant applies that
estimated elasticity to equities.

Run:  python src/volume_stress.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
q = pd.read_csv(ROOT / "data/processed/quarters.csv").set_index("quarter")
t = pd.read_csv(ROOT / "data/processed/take_rates.csv").set_index("quarter")
pnl = pd.read_csv(ROOT / "data/processed/vertical_pnl_summary_2026q2.csv").set_index("line")
OUT = ROOT / "outputs"

r = q.loc["2026Q2"]
TRADING = {"Options": r.options_rev, "Equities": r.equities_rev, "Crypto": r.crypto_rev,
           "Prediction markets": r.event_contracts_rev, "Other transaction": r.other_transaction_rev}
FIXED_REV = {"Subscriptions & Banking": r.other_rev, "Net interest": r.net_interest_rev}
var_cost_rate = r.brokerage_transaction_exp / r.transaction_rev_total          # ~8%
fixed_costs = r.total_opex - r.brokerage_transaction_exp
base_op = r.total_net_rev - r.total_opex

# Historical replay: peak (2021Q4) to trough revenue drop per line
hist = q.loc["2021Q4":"2023Q4"]
replay = {k: hist[c].min() / hist[c].iloc[0] - 1
          for k, c in [("Options", "options_rev"), ("Equities", "equities_rev"), ("Crypto", "crypto_rev")]}
replay["Prediction markets"] = replay["Options"]
replay["Other transaction"] = replay["Options"]

# Equities cushion: log(take rate) on log(volume), 2024Q1-2026Q2
e = t.join(q[["equity_notional_b"]]).dropna(subset=["equities_bps", "equity_notional_b"])
eq_elast = np.polyfit(np.log(e.equity_notional_b), np.log(e.equities_bps), 1)[0]

SCEN = {f"Volume -{p}%": {k: -p / 100 for k in TRADING} for p in (10, 20, 30, 50)}
SCEN["2022 replay"] = replay


def run(name, drops, cushion=False):
    rev = {}
    for k, base in TRADING.items():
        d = drops[k]
        rate_mult = (1 + d) ** eq_elast if (cushion and k == "Equities") else 1.0
        rev[k] = base * (1 + d) * rate_mult
    rev.update(FIXED_REV)
    trans = sum(rev[k] for k in TRADING)
    total = sum(rev.values())
    op = total - trans * var_cost_rate - fixed_costs
    row = {"scenario": name + (" (equities cushion)" if cushion else ""), **{f"rev_{k}": v for k, v in rev.items()},
           "total_revenue": total, "revenue_change_pct": (total / r.total_net_rev - 1) * 100,
           "operating_profit": op, "op_profit_change_pct": (op / base_op - 1) * 100,
           "operating_margin_pct": op / total * 100}
    row["profit_vs_revenue_multiple"] = row["op_profit_change_pct"] / row["revenue_change_pct"]
    return row


rows = [run("Q2 2026 actual", {k: 0 for k in TRADING})]
for n, d in SCEN.items():
    rows.append(run(n, d))
rows.append(run("Volume -30%", SCEN["Volume -30%"], cushion=True))
co = pd.DataFrame(rows)
co.to_csv(OUT / "volume_stress_company.csv", index=False)

# Per-vertical profit under a 30% volume drop (shared costs stay where they are)
vrows = []
for k in ["Options", "Equities", "Crypto", "Prediction markets", "Subscriptions & Banking"]:
    p = pnl.loc[k]
    d = -0.30 if k in TRADING else 0.0
    new_rev = p.revenue * (1 + d)
    direct = p.direct_costs * (1 + d) if k in TRADING else p.direct_costs
    op = new_rev - direct - p.shared_costs
    vrows.append({"vertical": k, "volume_sensitive": int(k in TRADING), "revenue_q2_2026": p.revenue,
                  "revenue_at_minus30": new_rev, "op_profit_q2_2026": p.operating_profit,
                  "op_profit_at_minus30": op, "op_margin_q2_2026": p.operating_margin * 100,
                  "op_margin_at_minus30": op / new_rev * 100,
                  "replay_volume_drop_pct": replay.get(k, 0) * 100})
ve = pd.DataFrame(vrows)
ve.to_csv(OUT / "volume_stress_verticals.csv", index=False)

# Break-even: how far can volume fall before operating profit reaches zero?
trans_rev = sum(TRADING.values())
breakeven_drop = base_op / (trans_rev * (1 - var_cost_rate)) * 100

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(f"Variable cost rate {var_cost_rate:.1%} of transaction revenue; fixed costs ${fixed_costs:.0f}M/qtr")
    print(f"Equities take-rate elasticity to volume: {eq_elast:.2f}")
    print("Replay drops:", {k: f"{v:.0%}" for k, v in replay.items()})
    print(co[["scenario", "total_revenue", "revenue_change_pct", "operating_profit", "op_profit_change_pct",
              "operating_margin_pct", "profit_vs_revenue_multiple"]].round(1).to_string(index=False))
    print()
    print(ve.round(1).to_string(index=False))
    print(f"\nOperating profit reaches zero if trading volume falls {breakeven_drop:.0f}% (all else equal)")
