"""
Charts for the research note (note/figures/). One consistent color per vertical across
every chart; grey for lines that are not analyzed.

Run:  python src/charts_note.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "note" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

q = pd.read_csv(ROOT / "data/processed/quarters.csv")
t = pd.read_csv(ROOT / "data/processed/take_rates.csv")
# The note analyzes data through Q2 2026; Q3 2026 is only used to score the forecast (chart 8).
q = q[q.quarter <= "2026Q2"]
t = t[t.quarter <= "2026Q2"]
pnl = pd.read_csv(ROOT / "data/processed/vertical_pnl_summary_2026q2.csv").set_index("line")
inc = pd.read_csv(ROOT / "data/processed/incremental_margin.csv")
rq = pd.read_csv(ROOT / "outputs/revenue_quality.csv").set_index("line")
sotp = pd.read_csv(ROOT / "outputs/sotp.csv")

# ---- style -----------------------------------------------------------------------
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
COL = {"Options": "#2a78d6", "Equities": "#eb6834", "Crypto": "#1baf7a",
       "Prediction markets": "#eda100", "Subscriptions & Banking": "#e87ba4",
       "Other transaction": "#c3c2b7", "Net interest": "#e1e0d9"}
VERTICALS = ["Options", "Equities", "Crypto", "Prediction markets", "Subscriptions & Banking"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": BASE,
                     "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})


def fig(w=10, h=5.2):
    f, ax = plt.subplots(figsize=(w, h), dpi=200)
    f.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    return f, ax


def titles(f, title, sub, src="Source: Robinhood earnings releases; author's analysis."):
    f.text(0.01, 0.965, title, fontsize=15, fontweight="bold", color=INK, va="top")
    f.text(0.01, 0.905, sub, fontsize=10.5, color=INK2, va="top")
    f.text(0.01, 0.015, src, fontsize=8.5, color=MUTED)


def save(f, name):
    f.savefig(FIG / name, facecolor=SURF)
    plt.close(f)


# ---- 1. revenue mix ----------------------------------------------------------------
d = q.set_index("quarter")
mix = pd.DataFrame({
    "Options": d.options_rev, "Equities": d.equities_rev, "Crypto": d.crypto_rev,
    "Prediction markets": d.event_contracts_rev.fillna(0),
    "Other transaction": d.other_transaction_rev.fillna(0),
    "Subscriptions & Banking": d.other_rev, "Net interest": d.net_interest_rev})
order = ["Options", "Equities", "Crypto", "Prediction markets", "Other transaction",
         "Subscriptions & Banking", "Net interest"]
f, ax = fig(10, 5.6)
x = np.arange(len(mix))
bottom = np.zeros(len(mix))
for k in order:
    ax.bar(x, mix[k], bottom=bottom, color=COL[k], width=0.78, edgecolor=SURF, linewidth=1)
    last = mix[k].iloc[-1]
    if last > 40:
        ax.text(x[-1] + 0.6, bottom[-1] + last / 2, f"{k}  ${last:.0f}M", va="center", fontsize=9, color=INK2)
    bottom += mix[k].values
ax.set_xticks(x[::2]); ax.set_xticklabels(mix.index[::2], rotation=0, fontsize=8.5)
ax.set_xlim(-0.8, len(mix) + 6.5)
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.yaxis.set_major_formatter(lambda v, _: f"${v/1000:.1f}B" if v else "0")
titles(f, "Revenue by line, quarterly", "Grey = not analyzed. 'Other transaction' includes prediction markets until Q2 2026, "
       "when Robinhood began reporting them separately.")
plt.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.1)
save(f, "fig1_revenue_mix.png")

# ---- 2. take rates -----------------------------------------------------------------
tr = t.dropna(subset=["options_usd_per_contract"]).set_index("quarter")
panels = [("Options", "options_usd_per_contract", "$ per contract", "{:.2f}"),
          ("Equities", "equities_bps", "bps of notional", "{:.2f}"),
          ("Crypto", "crypto_bps_app_only", "bps, retail app (solid) vs blended (dashed)", "{:.0f}"),
          ("Subscriptions & Banking", "other_rev_per_gold_sub_usd", "$ per Gold subscriber per year", "{:.0f}")]
f, axes = plt.subplots(1, 4, figsize=(12, 3.9), dpi=200)
f.patch.set_facecolor(SURF)
for ax, (name, col, unit, fmt) in zip(axes, panels):
    ax.set_facecolor(SURF)
    s = tr[col]
    ax.plot(range(len(s)), s.values, color=COL[name], lw=2.2, marker="o", ms=4)
    if name == "Crypto":
        ax.plot(range(len(s)), tr["crypto_bps_blended"].values, color=COL[name], lw=1.6, ls="--")
    ax.set_title(name, loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=20)
    ax.text(0, 1.03, unit, transform=ax.transAxes, fontsize=8, color=INK2, va="bottom")
    ax.set_xticks([0, len(s) - 1]); ax.set_xticklabels([s.index[0], s.index[-1]], fontsize=8)
    ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
    ax.text(len(s) - 1, s.iloc[-1], "  " + fmt.format(s.iloc[-1]), va="center", fontsize=9, color=INK)
    lo = 0 if name in ("Crypto", "Subscriptions & Banking") else None
    if lo is not None: ax.set_ylim(bottom=0)
f.text(0.01, 0.97, "What Robinhood earns per unit of activity", fontsize=15, fontweight="bold", color=INK, va="top")
f.text(0.01, 0.015, "Source: Robinhood earnings releases; author's analysis. Volumes first disclosed Q1 2024.", fontsize=8.5, color=MUTED)
plt.subplots_adjust(left=0.04, right=0.97, top=0.76, bottom=0.12, wspace=0.35)
save(f, "fig2_take_rates.png")

# ---- 3. margins --------------------------------------------------------------------
f, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), dpi=200, gridspec_kw={"width_ratios": [1.15, 1]})
f.patch.set_facecolor(SURF)
for a in (ax, ax2): a.set_facecolor(SURF)
y = np.arange(len(VERTICALS))[::-1]
for yi, v in zip(y, VERTICALS):
    m, lo, hi = pnl.loc[v, ["operating_margin", "min", "max"]] * 100
    ax.barh(yi, m, color=COL[v], height=0.6)
    ax.plot([lo, hi], [yi, yi], color=INK, lw=1.8)
    ax.text(max(m, hi) + 1.5, yi, f"{m:.0f}%  (${pnl.loc[v, 'operating_profit']:.0f}M)", va="center", fontsize=9.5, color=INK)
ax.set_yticks(y); ax.set_yticklabels(VERTICALS, color=INK); ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 70); ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.set_title("Share of revenue kept as operating profit, Q2 2026 (estimate)\nBlack line = range under alternative cost-split rules", loc="left", fontsize=10.5, color=INK2)
inc2 = inc[inc.quarter >= "2024Q2"]
ax2.plot(inc2.quarter, inc2.incremental_margin_adj * 100, color=INK, lw=2.2, marker="o", ms=5)
for xq, v in zip(inc2.quarter, inc2.incremental_margin_adj * 100):
    ax2.text(xq, v + 5.5, f"{v:.0f}¢", ha="center", fontsize=8.5, color=INK2)
ax2.set_ylim(0, 100); ax2.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}¢")
ax2.tick_params(axis="x", labelsize=8, rotation=45)
ax2.yaxis.grid(True, color=GRID); ax2.set_axisbelow(True)
ax2.set_title("For each extra $1 of revenue vs a year earlier,\nhow many cents became operating profit", loc="left", fontsize=10.5, color=INK2)
f.text(0.01, 0.97, "Trading keeps ~45% of revenue as profit, but new revenue now adds less profit", fontsize=15, fontweight="bold", color=INK, va="top")
f.text(0.01, 0.015, "Source: Robinhood earnings releases; author's cost allocation (see methodology).", fontsize=8.5, color=MUTED)
plt.subplots_adjust(left=0.19, right=0.98, top=0.77, bottom=0.17, wspace=0.3)
save(f, "fig3_margins.png")

# ---- 4. competitiveness -------------------------------------------------------------
comp = [("Options\n(contracts traded)", [("Robinhood", 50), ("IBKR", 17), ("Webull", 68)]),
        ("Equities\n($ traded or trades)", [("Robinhood", 85), ("Webull", 73), ("Schwab", 57), ("IBKR", 36)]),
        ("Crypto\n(retail volume)", [("Robinhood", -36), ("Coinbase", -38)]),
        ("Subscriptions & Banking\n(revenue)", [("Robinhood", 54), ("SoFi", 29), ("Coinbase", -12)])]
vcol = [COL["Options"], COL["Equities"], COL["Crypto"], COL["Subscriptions & Banking"]]
f, ax = fig(10, 4.8)
for i, ((label, pts), c) in enumerate(zip(comp, vcol)):
    yi = len(comp) - 1 - i
    xs = [p[1] for p in pts]
    ax.plot([min(xs), max(xs)], [yi, yi], color=BASE, lw=1.5, zorder=1)
    for name, val in pts:
        hood = name == "Robinhood"
        ax.scatter(val, yi, s=140 if hood else 70, color=c if hood else SURF, edgecolor=c if hood else MUTED,
                   linewidth=2, zorder=3)
        off = {"Schwab": -0.46}.get(name, -0.33)
        ax.text(val, yi + (0.25 if hood else off), f"{name} {val:+d}%", ha="center", fontsize=8.5,
                color=INK if hood else INK2, fontweight="bold" if hood else "normal")
ax.axvline(0, color=BASE, lw=1)
ax.set_yticks(range(len(comp))); ax.set_yticklabels([c[0] for c in comp][::-1], color=INK, fontsize=9.5)
ax.tick_params(axis="y", length=0)
ax.set_xlim(-55, 100); ax.set_xticks([-40, -20, 0, 20, 40, 60, 80, 100]); ax.set_ylim(-0.7, len(comp) - 0.4)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%")
ax.set_xlabel("Growth vs a year earlier", fontsize=9.5, color=INK2)
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
titles(f, "Robinhood is growing faster than its large competitors",
       "Growth from Q2 2025 to Q2 2026 in trading activity (or revenue, for Subscriptions & Banking).",
       "Source: company earnings releases. Equities: dollar value traded for Robinhood and Webull; number of trades for Schwab and IBKR.")
plt.subplots_adjust(left=0.2, right=0.95, top=0.82, bottom=0.17)
save(f, "fig4_competition.png")

# ---- 5. trading-volume stress test ---------------------------------------------------
co = pd.read_csv(ROOT / "outputs/volume_stress_company.csv")
ve = pd.read_csv(ROOT / "outputs/volume_stress_verticals.csv").set_index("vertical")
f, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=200, gridspec_kw={"width_ratios": [1.1, 1]})
f.patch.set_facecolor(SURF)
for a in (ax, ax2): a.set_facecolor(SURF)
order = [("Volume -10%", "Trading\n-10%"), ("Volume -20%", "Trading\n-20%"), ("Volume -30%", "Trading\n-30%"),
         ("Volume -50%", "Trading\n-50%"), ("2022 replay", "Repeat\nof 2022")]
cs = co.set_index("scenario")
xx = np.arange(len(order))
rev = [cs.loc[k, "revenue_change_pct"] for k, _ in order]
prof = [cs.loc[k, "op_profit_change_pct"] for k, _ in order]
ax.bar(xx - 0.19, rev, width=0.36, color="#c3c2b7", label="Revenue")
ax.bar(xx + 0.19, prof, width=0.36, color=INK2, label="Operating profit")
for xi, rv, pv in zip(xx, rev, prof):
    ax.text(xi - 0.19, rv - 2, f"{rv:.0f}%", ha="center", va="top", fontsize=8.5, color=INK2)
    ax.text(xi + 0.19, pv - 2, f"{pv:.0f}%", ha="center", va="top", fontsize=8.5, color=INK, fontweight="bold")
ax.set_xticks(xx); ax.set_xticklabels([l for _, l in order], fontsize=9, color=INK)
ax.tick_params(axis="x", length=0)
ax.set_ylim(-72, 5); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True); ax.axhline(0, color=BASE, lw=1)
ax.legend(loc="lower left", frameon=False, fontsize=9)
ax.set_title("How much revenue and operating profit would fall,\ncompared with Q2 2026, in each scenario", loc="left", fontsize=10.5, color=INK2)
vs = ["Options", "Equities", "Crypto", "Prediction markets", "Subscriptions & Banking"]
y = np.arange(len(vs))[::-1]
ax2.barh(y + 0.18, ve.loc[vs, "op_profit_q2_2026"], height=0.34, color=[COL[v] for v in vs])
ax2.barh(y - 0.18, ve.loc[vs, "op_profit_at_minus30"], height=0.34, color=[COL[v] for v in vs], alpha=0.35)
for yi, v in zip(y, vs):
    a, b = ve.loc[v, ["op_profit_q2_2026", "op_profit_at_minus30"]]
    ax2.text(a + 2, yi + 0.18, f"${a:.0f}M", va="center", fontsize=8.5, color=INK2)
    ax2.text(b + 2, yi - 0.18, f"${b:.0f}M" + (f" ({b/a-1:+.0%})" if v != "Subscriptions & Banking" else " (unchanged)"),
             va="center", fontsize=8.5, color=INK, fontweight="bold")
ax2.set_yticks(y); ax2.set_yticklabels(vs, color=INK, fontsize=9.5); ax2.tick_params(axis="y", length=0)
ax2.set_xlim(0, 215); ax2.xaxis.set_major_formatter(lambda v, _: f"${v:.0f}M")
ax2.xaxis.grid(True, color=GRID); ax2.set_axisbelow(True)
ax2.set_title("Estimated operating profit per business, per quarter:\nQ2 2026 actual (dark) vs if trading fell 30% (light)", loc="left", fontsize=10.5, color=INK2)
f.text(0.01, 0.97, "If customers trade 30% less, Robinhood's operating profit falls 37%", fontsize=15, fontweight="bold", color=INK, va="top")
f.text(0.01, 0.015, "Starting point: Q2 2026. Robinhood earns the same per trade; only exchange and clearing fees (8% of trading revenue) shrink with trading,\n"
       "all other costs stay the same. Subscriptions & Banking and net interest unchanged. Repeat of 2022 = each business falls as much as it did in 2022-23.", fontsize=8, color=MUTED)
plt.subplots_adjust(left=0.07, right=0.98, top=0.8, bottom=0.2, wspace=0.42)
save(f, "fig5_volume_stress.png")

# ---- 6. valuation waterfall -----------------------------------------------------------
s = sotp.copy()
s["short"] = s.line.str.replace(" (not analyzed)", "", regex=False)
s = pd.concat([s, pd.DataFrame([{"short": "Net cash", "value_base_b": 3.16, "value_low_b": 3.16, "value_high_b": 3.16}])])
f, ax = fig(10.5, 5.4)
run = 0
for i, r in enumerate(s.itertuples()):
    c = COL.get(r.short, MUTED) if r.short in VERTICALS else "#c3c2b7"
    ax.bar(i, r.value_base_b, bottom=run, color=c, width=0.7)
    ax.text(i, run + r.value_base_b + 1, f"${r.value_base_b:.1f}B", ha="center", fontsize=9, color=INK)
    run += r.value_base_b
ax.bar(len(s), run, color=INK2, width=0.7)
ax.text(len(s), run + 1, f"${run:.0f}B", ha="center", fontsize=10, color=INK, fontweight="bold")
ax.bar(len(s) + 1, 88.89, color=INK, width=0.7)
ax.text(len(s) + 1, 90, "$89B", ha="center", fontsize=10, color=INK, fontweight="bold")
ax.annotate("", xy=(len(s) + 0.5, 88.89), xytext=(len(s) + 0.5, run),
            arrowprops=dict(arrowstyle="<->", color="#e34948", lw=1.6))
ax.text(len(s) + 0.4, (run + 88.89) / 2 + 6, f"+${88.89 - run:.0f}B paid\nfor growth ", fontsize=9.5, color="#e34948", va="center", ha="right")
labels = [x.replace(" & ", " &\n").replace("Prediction markets", "Prediction\nmarkets").replace("Other transaction", "Other\ntransaction")
          .replace("Net interest", "Net\ninterest") for x in s.short] + ["Sum of\nparts", "Market\ncap"]
ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=8.5, color=INK)
ax.tick_params(axis="x", length=0)
ax.set_ylim(0, 100); ax.yaxis.set_major_formatter(lambda v, _: f"${v:.0f}B")
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
titles(f, "Valuation: the parts add up to \\$57B; the market pays \\$89B",
       "Each line valued at its closest listed peers' EV / FY2027 revenue (base case). Low-high range: \\$30B-\\$82B.",
       "Source: Robinhood, peer filings, stockanalysis.com / Yahoo Finance (Oct 16, 2026 close); author's analysis.")
plt.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.17)
save(f, "fig6_sotp.png")

print("charts written:", sorted(p.name for p in FIG.glob("*.png")))

# ---- 8. Q3 2026 forecast vs actual ------------------------------------------------------
sc_path = ROOT / "outputs/q3_2026_scorecard.csv"
if sc_path.exists():
    sc = pd.read_csv(sc_path)
    lines8 = ["Options", "Equities", "Crypto", "Prediction markets", "Subscriptions & Banking"]
    sc = sc.set_index("line").loc[lines8]
    f, ax = fig(10, 4.8)
    y = np.arange(len(lines8))[::-1]
    for yi, v in zip(y, lines8):
        r = sc.loc[v]
        ax.plot([r.low, r.high], [yi, yi], color=COL[v], lw=10, alpha=0.3, solid_capstyle="butt")
        ax.plot([r.forecast, r.forecast], [yi - 0.22, yi + 0.22], color=INK2, lw=2)
        ax.scatter(r.actual, yi, s=110, color=COL[v], edgecolor=INK, linewidth=1.2, zorder=3)
        verdict = "in range" if r.within_range == "yes" else f"{r.within_range} range"
        ax.text(max(r.high, r.actual) + 8, yi, f"reported \\${r.actual:.0f}M vs forecast \\${r.forecast:.0f}M  ({verdict})",
                va="center", fontsize=9, color=INK)
    ax.set_yticks(y); ax.set_yticklabels(lines8, color=INK); ax.tick_params(axis="y", length=0)
    ax.set_xlim(90, 640); ax.xaxis.set_major_formatter(lambda v, _: f"${v:.0f}M")
    ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
    titles(f, "Q3 2026: forecast vs reported revenue",
           "Shaded bar = forecast range, grey tick = forecast, dot = reported. Total: \\$1,432M forecast vs \\$1,424M reported (-0.6%).",
           "Forecast made Oct 18, 2026; results reported Oct 27, 2026. Source: Robinhood Q3 2026 earnings release.")
    plt.subplots_adjust(left=0.2, right=0.98, top=0.82, bottom=0.12)
    save(f, "fig8_q3_scorecard.png")

# ---- 9. my forecast vs Zacks consensus: errors by line ------------------------------------
vz_path = ROOT / "outputs/q3_2026_vs_zacks.csv"
if vz_path.exists():
    vz = pd.read_csv(vz_path)
    vz["short"] = vz.line.str.replace(" (not analyzed)", "", regex=False).str.replace("TOTAL NET REVENUE", "Total revenue")
    f, ax = fig(10, 5.2)
    y = np.arange(len(vz))[::-1]
    ax.barh(y + 0.19, vz.my_error_m, height=0.36, color="#2a78d6", label="My forecast")
    ax.barh(y - 0.19, vz.zacks_error_m, height=0.36, color="#c3c2b7", label="Zacks consensus")
    for yi, a_, b_ in zip(y, vz.my_error_m, vz.zacks_error_m):
        ax.text(a_ + (1 if a_ >= 0 else -1), yi + 0.19, f"{a_:+.0f}", va="center", ha="left" if a_ >= 0 else "right", fontsize=8.5, color=INK)
        ax.text(b_ + (1 if b_ >= 0 else -1), yi - 0.19, f"{b_:+.0f}", va="center", ha="left" if b_ >= 0 else "right", fontsize=8.5, color=INK2)
    ax.axvline(0, color=INK2, lw=1)
    ax.axhline(0.5, color=BASE, lw=1, ls="--")
    ax.set_yticks(y); ax.set_yticklabels(vz.short, color=INK, fontsize=9.5); ax.tick_params(axis="y", length=0)
    ax.set_xlim(-35, 25); ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}" if v else "0")
    ax.set_xlabel("Forecast minus reported revenue, $M (right = too high, left = too low)", fontsize=9, color=INK2)
    ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    titles(f, "My total was closer than Zacks, but Zacks was closer on every line",
           "Q3 2026 revenue forecast errors by line. My errors offset each other; adding them up without signs: \\$82M for me, \\$52M for Zacks.",
           "Zacks consensus from its Q3 preview (day before the report); prediction markets implied from its transaction-revenue estimate. Reported: Robinhood, Oct 27, 2026.")
    plt.subplots_adjust(left=0.22, right=0.97, top=0.83, bottom=0.17)
    save(f, "fig9_vs_zacks.png")
