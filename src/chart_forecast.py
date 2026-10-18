"""Chart: Q2 2026 actual vs Q3 2026 forecast (with range), per vertical."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
f = pd.read_csv(ROOT / "outputs/q3_2026_forecast.csv").head(5)
q2 = {"Options": 342, "Equities": 129, "Crypto": 100, "Prediction markets": 156, "Subscriptions & Banking": 143}

SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
C_Q2, C_Q3 = "#c3c2b7", "#2a78d6"   # context (actual) in neutral, focus (forecast) in series-1 blue

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
fig, ax = plt.subplots(figsize=(12, 6.75), dpi=150)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)

labels = f["vertical"].tolist()
y = range(len(labels))[::-1]
h = 0.34
for yi, (_, r) in zip(y, f.iterrows()):
    a = q2[r.vertical]
    ax.barh(yi + h / 2 + 0.02, a, height=h, color=C_Q2)
    ax.barh(yi - h / 2 - 0.02, r.rev_base, height=h, color=C_Q3)
    ax.plot([r.rev_low, r.rev_high], [yi - h / 2 - 0.02] * 2, color=INK, lw=2, solid_capstyle="round")
    for x in (r.rev_low, r.rev_high):
        ax.plot([x, x], [yi - h / 2 - 0.1, yi - h / 2 + 0.06], color=INK, lw=2)
    ax.text(a + 6, yi + h / 2 + 0.02, f"${a}M", va="center", color=INK2, fontsize=12)
    ax.text(r.rev_high + 8, yi - h / 2 - 0.02, f"${r.rev_base:.0f}M", va="center", color=INK, fontsize=12, fontweight="bold")

ax.set_yticks(list(y)); ax.set_yticklabels(labels, color=INK)
ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 520)
ax.xaxis.grid(True, color=GRID, lw=1); ax.set_axisbelow(True)
ax.tick_params(axis="x", colors=MUTED)
ax.xaxis.set_major_formatter(lambda v, _: f"${v:.0f}M")
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(BASE)

fig.text(0.02, 0.95, "Robinhood Q3 2026 revenue forecast, by business line", fontsize=19, fontweight="bold", color=INK)
fig.text(0.02, 0.905, "Made Oct 18, 2026, before the Oct 27 report. Black whisker = forecast range.", fontsize=12.5, color=INK2)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C_Q2, label="Q2 2026 actual"), Patch(color=C_Q3, label="Q3 2026 forecast")],
          loc="lower right", frameon=False, fontsize=12, labelcolor=INK)
fig.text(0.02, 0.025, "Forecast = monthly trading activity x revenue per unit (take rate). Excludes net interest. Source: Robinhood earnings & operating data releases.",
         fontsize=10, color=MUTED)
plt.subplots_adjust(left=0.2, right=0.97, top=0.86, bottom=0.11)
fig.savefig(ROOT / "outputs/charts/q3_2026_forecast.png", facecolor=SURF)
