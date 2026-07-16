from pathlib import Path
import csv

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np


ROOT = Path(__file__).resolve().parent

rounds = np.arange(1, 6)
strict = np.array([0.0, 22.2, 33.3, 33.3, 33.3])
preservation_evidence = np.array([66.7, 66.7, 88.9, 88.9, 88.9])
active_seeds = [9, 9, 7, 6, 6]
strict_counts = ["0/9", "2/9", "3/9", "3/9", "3/9"]
evidence_counts = ["6/9", "6/9", "8/9", "8/9", "8/9"]

with (ROOT / "rq4_token_usage_by_round.csv").open(newline="", encoding="utf-8") as handle:
    token_rows = list(csv.DictReader(handle))

api_calls = np.array([int(row["api_calls"]) for row in token_rows], dtype=float)
total_tokens_per_call = np.array(
    [int(row["total_tokens"]) for row in token_rows], dtype=float
) / api_calls / 1000.0

soft_blues = LinearSegmentedColormap.from_list(
    "soft_blues",
    ["#EEF4F8", "#CADCE8", "#9EC4DA", "#6AA6C9", "#3F89B7"],
)

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"],
        "font.size": 7.4,
        "axes.labelsize": 7.8,
        "xtick.labelsize": 7.1,
        "ytick.labelsize": 7.1,
        "legend.fontsize": 6.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

fig = plt.figure(figsize=(3.48, 2.72))
grid = fig.add_gridspec(2, 1, height_ratios=[7.0, 0.72], hspace=0.02)
ax = fig.add_subplot(grid[0])
heat_ax = fig.add_subplot(grid[1], sharex=ax)

observed_rounds = rounds
ax.fill_between(
    observed_rounds,
    0,
    preservation_evidence,
    color="#5B83B4",
    alpha=0.10,
    zorder=0,
)
ax.fill_between(
    observed_rounds,
    0,
    strict,
    color="#4C78FF",
    alpha=0.16,
    zorder=1,
)

ax.plot(
    rounds,
    strict,
    color="#4C78FF",
    marker="o",
    markersize=4.2,
    markerfacecolor="#4C78FF",
    markeredgewidth=0.8,
    linewidth=1.35,
    label="Strict recovery",
    zorder=3,
)
ax.plot(
    rounds,
    preservation_evidence,
    color="#4E79A7",
    marker="s",
    markersize=4.0,
    markerfacecolor="#4E79A7",
    markeredgewidth=0.8,
    linewidth=1.35,
    linestyle="-",
    label="Inclusive preservation evidence",
    zorder=3,
)

for x, y, label in zip(rounds, strict, strict_counts):
    ax.annotate(
        label,
        (x, y),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        va="bottom",
        color="#4C78FF",
        fontsize=6.9,
    )
for x, y, label in zip(rounds, preservation_evidence, evidence_counts):
    ax.annotate(
        label,
        (x, y),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        va="bottom",
        color="#4E79A7",
        fontsize=6.9,
    )

ax.set_xlim(0.5, 5.5)
ax.set_ylim(0, 104)
ax.set_ylabel("Cumulative seeds (%)")
ax.set_xticks(rounds)
ax.tick_params(axis="x", labelbottom=False)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0", "25", "50", "75", "100"])
ax.grid(axis="both", color="#C7CDD6", linewidth=0.55, linestyle=(0, (2, 2)), alpha=0.8, zorder=0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.7)
ax.spines["bottom"].set_linewidth(0.7)
ax.tick_params(width=0.7, length=2.5)
ax.legend(
    loc="center right",
    bbox_to_anchor=(0.985, 0.58),
    ncol=1,
    frameon=True,
    facecolor="white",
    edgecolor="#B8B8B8",
    framealpha=0.88,
    borderpad=0.28,
    labelspacing=0.25,
    handlelength=1.8,
    handletextpad=0.42,
)

token_strip = total_tokens_per_call[np.newaxis, :]
heat_ax.imshow(
    token_strip,
    cmap=soft_blues,
    vmin=4.8,
    vmax=13.5,
    aspect="auto",
    interpolation="nearest",
    extent=(0.5, 5.5, 0, 1),
)
for boundary in np.arange(1.5, 5.0, 1.0):
    heat_ax.axvline(
        boundary,
        color="#AAB4C0",
        linewidth=0.45,
        alpha=0.65,
        zorder=3,
    )
for x, value in zip(rounds, total_tokens_per_call):
    heat_ax.text(
        x,
        0.5,
        f"{value:.1f}k",
        ha="center",
        va="center",
        color="white" if value >= 9.5 else "#254E77",
        fontsize=6.3,
        fontweight="bold",
    )

heat_ax.set_yticks([0.5])
heat_ax.set_yticklabels(["Mean API\ntokens/call"], fontsize=5.9)
heat_ax.set_xticks(rounds)
heat_ax.set_xticklabels([f"Rd{i}\n{n} seeds" for i, n in zip(rounds, active_seeds)])
heat_ax.set_xlabel("Iteration", labelpad=1.5)
heat_ax.tick_params(axis="x", width=0.6, length=0, pad=2)
heat_ax.tick_params(axis="y", width=0, length=0, pad=3)
for spine in heat_ax.spines.values():
    spine.set_color("#AAB4C0")
    spine.set_linewidth(0.5)

fig.subplots_adjust(left=0.18, right=0.99, top=0.97, bottom=0.20)
fig.savefig(ROOT / "rq4_iteration_trajectory.png", dpi=240, bbox_inches="tight", pad_inches=0.02)
plt.close(fig)
