from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "rq4_two_candidate_token_plot_data.csv"
OUT_PNG = ROOT / "rq4_token_distribution.png"
SEEDS = ["024", "037", "039", "061", "069", "094", "112", "118", "147"]
ROUNDS = [1, 2, 3, 4, 5]


def read_rows() -> list[dict[str, str]]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


rows = read_rows()
active = [row for row in rows if row["active"].lower() == "true"]
request_values = np.array(
    [float(row["request_tokens_per_actual_context_object"]) for row in active]
)
response_values = np.array(
    [float(row["response_tokens_per_generated_candidate"]) / 1000.0 for row in active]
)

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"],
        "font.size": 8.0,
        "axes.labelsize": 8.6,
        "xtick.labelsize": 7.3,
        "ytick.labelsize": 7.1,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

soft_blues = LinearSegmentedColormap.from_list(
    "soft_blues",
    ["#EEF4F8", "#D6E5EE", "#B8D3E2", "#8EBBD3", "#5D9FC3"],
)
norm = LogNorm(vmin=float(request_values.min()), vmax=float(request_values.max()))

fig = plt.figure(figsize=(6.55, 4.15), dpi=180)
ax = fig.add_subplot(111, projection="3d")
ax.set_position([0.0, 0.005, 0.82, 0.985])

dx, dy = 0.54, 0.54
for row in rows:
    round_index = int(row["round"]) - 1
    seed_index = SEEDS.index(row["case_id"].split("_")[1])
    x0, y0 = round_index - dx / 2, seed_index - dy / 2
    if row["active"].lower() != "true":
        vertices = [[
            (x0, y0, 0.003),
            (x0 + dx, y0, 0.003),
            (x0 + dx, y0 + dy, 0.003),
            (x0, y0 + dy, 0.003),
        ]]
        tile = Poly3DCollection(
            vertices,
            facecolors="#F1F2F3",
            edgecolors="#D9DDE0",
            linewidths=0.25,
            alpha=0.86,
        )
        ax.add_collection3d(tile)
        continue

    height = float(row["response_tokens_per_generated_candidate"]) / 1000.0
    request = float(row["request_tokens_per_actual_context_object"])
    ax.bar3d(
        x0,
        y0,
        0,
        dx,
        dy,
        height,
        color=soft_blues(norm(request)),
        edgecolor="#4A5861",
        linewidth=0.30,
        shade=False,
        alpha=0.98,
    )

ax.set_xlim(-0.55, len(ROUNDS) - 0.40)
ax.set_ylim(-0.55, len(SEEDS) - 0.40)
ax.set_zlim(0, max(1.02, float(response_values.max()) * 1.08))
ax.set_xticks(np.arange(len(ROUNDS)))
ax.set_xticklabels([f"Rd{round_number}" for round_number in ROUNDS])
ax.set_yticks(np.arange(len(SEEDS)))
ax.set_yticklabels(SEEDS)
ax.set_xlabel("")
ax.set_ylabel("Seed case", labelpad=6)
ax.set_zlabel("")
ax.set_box_aspect((1.55, 1.55, 0.95), zoom=1.19)
ax.view_init(elev=25, azim=-57)
ax.grid(True)
for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
    axis.pane.set_facecolor((0.985, 0.985, 0.985, 0.12))
    axis.pane.set_edgecolor("#CFD4D8")

scalar = mpl.cm.ScalarMappable(norm=norm, cmap=soft_blues)
scalar.set_array([])
cax = fig.add_axes([0.819, 0.245, 0.026, 0.53])
colorbar = fig.colorbar(scalar, cax=cax)
colorbar.ax.set_title("Request/context\n(log)", fontsize=7.1, pad=4)
colorbar.ax.tick_params(labelsize=6.8, length=2.0)
fig.text(
    0.012,
    0.52,
    "Response tokens / candidate (k)",
    rotation=90,
    va="center",
    ha="center",
    fontsize=8.0,
)

fig.savefig(OUT_PNG, dpi=260, bbox_inches="tight", pad_inches=0.015)
plt.close(fig)

print(OUT_PNG)
