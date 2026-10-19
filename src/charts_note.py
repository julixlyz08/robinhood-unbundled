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
ax.set_title("Estimated operating margin, Q2 2026\n(black line = range across cost scenarios)", loc="left", fontsize=10.5, color=INK2)
inc2 = inc[inc.quarter >= "2024Q2"]
ax2.plot(inc2.quarter, inc2.incremental_margin_adj * 100, color=INK, lw=2.2, marker="o", ms=5)
for xq, v in zip(inc2.quarter, inc2.incremental_margin_adj * 100):
    ax2.text(xq, v + 5.5, f"{v:.0f}%", ha="center", fontsize=8.5, color=INK2)
ax2.set_ylim(0, 100); ax2.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax2.tick_params(axis="x", labelsize=8, rotation=45)
ax2.yaxis.grid(True, color=GRID); ax2.set_axisbelow(True)
ax2.set_title("Incremental margin: share of each new revenue $\nreaching operating profit (YoY, one-offs removed)", loc="left", fontsize=10.5, color=INK2)
f.text(0.01, 0.97, "Profitability: trading is highly profitable; operating leverage is fading", fontsize=15, fontweight="bold", color=INK, va="top")
f.text(0.01, 0.015, "Source: Robinhood earnings releases; author's cost allocation (see methodology).", fontsize=8.5, color=MUTED)
plt.subplots_adjust(left=0.19, right=0.98, top=0.77, bottom=0.17, wspace=0.3)
save(f, "fig3_margins.png")

# ---- 4. competitiveness -------------------------------------------------------------
comp = [("Options\n(contracts traded)", [("Robinhood", 50), ("IBKR", 17), ("Webull", 68)]),
        ("Equities\n(notional or trades)", [("Robinhood", 85), ("Webull", 73), ("Schwab", 57), ("IBKR", 36)]),
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
ax.set_xlim(-55, 100); ax.set_ylim(-0.7, len(comp) - 0.4)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%")
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
titles(f, "Competitiveness: growth vs rivals, Q2 2026 vs Q2 2025",
       "Filled dot = Robinhood. Robinhood grows faster than the large incumbents in every trading line.",
       "Source: company earnings releases; author's analysis. Schwab and IBKR equities = daily average trades (all products).")
plt.subplots_adjust(left=0.2, right=0.98, top=0.82, bottom=0.12)
save(f, "fig4_competition.png")

# ---- 5. revenue quality --------------------------------------------------------------
lines = ["Options", "Equities", "Crypto", "Subscriptions & Banking"]
f, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), dpi=200, gridspec_kw={"width_ratios": [1.3, 1]})
f.patch.set_facecolor(SURF)
for a in (ax, ax2): a.set_facecolor(SURF)
y = np.arange(len(lines))[::-1]
parts = [("steady_growth_share", "Steady growth", "#2a78d6"), ("market_mood_share", "Market mood (VIX, Bitcoin)", "#eb6834"),
         ("unexplained_share", "Other (launches, one-offs)", "#c3c2b7")]
left = np.zeros(len(lines))
for col, lab, c in parts:
    vals = rq.loc[lines, col].values * 100
    ax.barh(y, vals, left=left, color=c, height=0.6, edgecolor=SURF, linewidth=2, label=lab)
    for yi, l, v in zip(y, left, vals):
        if v >= 9: ax.text(l + v / 2, yi, f"{v:.0f}%", ha="center", va="center", fontsize=9, color="white" if c != "#c3c2b7" else INK)
    left += vals
ax.set_yticks(y); ax.set_yticklabels(lines, color=INK); ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 100); ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=8.5)
ax.set_title("What drives each line's ups and downs (2021–2026)", loc="left", fontsize=10.5, color=INK2)
imp = rq.loc[lines, "btc_minus30_change_m"]
ax2.barh(y, imp.values, color=[COL[l] for l in lines], height=0.6)
for yi, v, p in zip(y, imp.values, rq.loc[lines, "btc_minus30_change_pct"].values):
    ax2.text(v - 1.5, yi, f"-${abs(v):.0f}M ({p:.0f}%)", ha="right", va="center", fontsize=9, color=INK)
ax2.set_yticks(y); ax2.set_yticklabels([]); ax2.tick_params(axis="y", length=0)
ax2.set_xlim(-80, 0); ax2.set_xticks([-60, -40, -20, 0]); ax2.xaxis.set_major_formatter(lambda v, _: f"-${abs(v):.0f}M" if v else "0")
ax2.xaxis.grid(True, color=GRID); ax2.set_axisbelow(True)
ax2.set_title("Quarterly revenue impact if Bitcoin falls 30%\n(total: about -$135M, -19%)", loc="left", fontsize=10.5, color=INK2)
f.text(0.01, 0.97, "Revenue quality: Bitcoin, not the VIX, is the swing factor", fontsize=15, fontweight="bold", color=INK, va="top")
f.text(0.01, 0.015, "Source: Robinhood earnings releases, Yahoo Finance; log regression of quarterly revenue on trend, VIX and Bitcoin (21 quarters).",
       fontsize=8.5, color=MUTED)
plt.subplots_adjust(left=0.19, right=0.98, top=0.8, bottom=0.22, wspace=0.12)
save(f, "fig5_revenue_quality.png")

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
