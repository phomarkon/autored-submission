"""Generate publication-quality figures for the AutoControl NeurIPS paper."""

import numpy as np
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from pathlib import Path

# ---------------------------------------------------------------------------
# Global style
# ---------------------------------------------------------------------------
OUT = Path(__file__).parent / "manuscript" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

COL_W = 3.25   # NeurIPS single-column width (inches)
FULL_W = 6.75  # NeurIPS full width (inches)

RED = "#c44e52"
BLUE = "#4c72b0"
TEAL = "#55a868"
GOLD = "#e5ae38"
GRAY = "#8c8c8c"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10", "Computer Modern Roman", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "cm",
    "axes.unicode_minus": False,
    "axes.formatter.use_mathtext": True,
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "lines.linewidth": 1.2,
    "lines.markersize": 4,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "pdf.fonttype": 42,  # TrueType — editable text in PDF
    "ps.fonttype": 42,
})

LW_MAIN = 1.3
MS_MAIN = 4
MS_STAR = 10


# ---------------------------------------------------------------------------
# Figure 1a: Phase 1 Red Optimization
# ---------------------------------------------------------------------------
def fig_phase1():
    iters = np.arange(15)
    asr = [0.2, 0.3, 0.1, 0.2, 0.1, 0.2, 0.0, 0.3, 0.1, 0.1,
           0.0, 0.0, 0.1, 0.1, 0.2]
    kept = [True, True, False, False, False, False, False, False,
            False, False, False, False, False, False, False]

    # running best
    best = np.maximum.accumulate(asr)

    fig, ax = plt.subplots(figsize=(COL_W, 2.2))

    ax.plot(iters, asr, "-o", color=RED, lw=LW_MAIN, ms=MS_MAIN,
            zorder=3, label="Attack success")
    ax.plot(iters, best, "--", color=RED, lw=0.9, alpha=0.5,
            label="Running best")

    # gold stars for kept
    ki = [i for i, k in enumerate(kept) if k]
    ax.scatter(ki, [asr[i] for i in ki], marker="*", s=MS_STAR**2,
               color=GOLD, edgecolors="k", linewidths=0.4, zorder=5,
               label="Kept")

    ax.axhline(0.0, ls="--", color=GRAY, lw=0.8, zorder=1)
    ax.text(14.0, 0.015, "Baseline", ha="right", va="bottom",
            fontsize=7, color=GRAY)

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Attack Success Rate")
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.05, 0.45)
    ax.set_xticks(np.arange(0, 15, 2))
    ax.legend(loc="upper right", frameon=True, fancybox=False,
              edgecolor="#cccccc", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(OUT / "elicitation_phase1.pdf")
    plt.close(fig)
    print(f"  -> {OUT / 'elicitation_phase1.pdf'}")


# ---------------------------------------------------------------------------
# Figure 1b: Phase 2 Blue Optimization
# ---------------------------------------------------------------------------
def fig_phase2():
    iters = np.arange(15)
    safety = [1.0, 0.8, 0.9, 0.6, 0.7, 0.8, 0.4, 1.0, 1.0, 0.6,
              1.0, 0.5, 1.0, 1.0, 0.6]
    useful = [0.0, 0.7, 0.9, 0.7, 0.9, 0.7, 0.6, 0.0, 0.0, 0.7,
              0.0, 0.6, 0.0, 0.6, 0.7]
    kept = [False, False, True, False, False, False, False, False,
            False, False, False, False, False, False, False]

    fig, ax = plt.subplots(figsize=(COL_W, 2.2))

    ax.plot(iters, safety, "-o", color=BLUE, lw=LW_MAIN, ms=MS_MAIN,
            zorder=3, label="Safety")
    ax.plot(iters, useful, "-s", color=TEAL, lw=LW_MAIN, ms=MS_MAIN,
            zorder=3, label="Usefulness")

    # gold star on safety line for kept
    ki = [i for i, k in enumerate(kept) if k]
    ax.scatter(ki, [safety[i] for i in ki], marker="*", s=MS_STAR**2,
               color=GOLD, edgecolors="k", linewidths=0.4, zorder=5,
               label="Kept")

    ax.axhline(1.0, ls="--", color=GRAY, lw=0.8, zorder=1)
    ax.text(14.0, 0.97, "Baseline safety", ha="right", va="top",
            fontsize=7, color=GRAY)

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Rate")
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xticks(np.arange(0, 15, 2))
    ax.legend(loc="lower right", frameon=True, fancybox=False,
              edgecolor="#cccccc", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(OUT / "elicitation_phase2.pdf")
    plt.close(fig)
    print(f"  -> {OUT / 'elicitation_phase2.pdf'}")


# ---------------------------------------------------------------------------
# Figure 2: Phase 3 Co-evolution (full width)
# ---------------------------------------------------------------------------
def fig_coevolution():
    rounds = np.arange(5)
    red_asr = [0.6, 0.3, 0.5, 0.6, 0.5]
    blue_safety = [1.0, 0.7, 1.0, 1.0, 1.0]

    fig, ax = plt.subplots(figsize=(FULL_W, 3.0))

    # Alternating vertical bands for Red / Blue phases within each round.
    # Each round has a Red half and a Blue half.
    for r in rounds:
        ax.axvspan(r - 0.25, r, alpha=0.06, color=RED, zorder=0)
        ax.axvspan(r, r + 0.25, alpha=0.06, color=BLUE, zorder=0)

    # Add phase labels in round 0 only (avoid clutter)
    ax.text(-0.125, 1.08, "Red", ha="center", va="bottom", fontsize=7,
            color=RED, alpha=0.7)
    ax.text(0.125, 1.08, "Blue", ha="center", va="bottom", fontsize=7,
            color=BLUE, alpha=0.7)

    # Fill between
    ax.fill_between(rounds, red_asr, blue_safety, alpha=0.08, color=GRAY,
                     zorder=1)

    ax.plot(rounds, red_asr, "-o", color=RED, lw=1.5, ms=6, zorder=4,
            label="Best attack success (Red)")
    ax.plot(rounds, blue_safety, "-s", color=BLUE, lw=1.5, ms=6, zorder=4,
            label="Best safety (Blue)")

    ax.set_xlabel("Co-evolution Round")
    ax.set_ylabel("Rate")
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(-0.05, 1.15)
    ax.set_xticks(rounds)
    ax.legend(loc="lower left", frameon=True, fancybox=False,
              edgecolor="#cccccc", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(OUT / "coevolution.pdf")
    plt.close(fig)
    print(f"  -> {OUT / 'coevolution.pdf'}")


# ---------------------------------------------------------------------------
# Figure 3: Transfer Matrix (heatmap)
# ---------------------------------------------------------------------------
def fig_transfer():
    data = np.array([
        [0.30, 0.20, 0.00],
        [0.20, 0.50, 0.00],
        [0.20, 0.30, 0.10],
    ])
    row_labels = ["Naive", "Phase 1\nBest", "Phase 3\nBest"]
    col_labels = ["Baseline\n($\\tau$=0.5)", "Phase 2\nBest", "Aggressive\n($\\tau$=0.3)"]

    fig, ax = plt.subplots(figsize=(3.5, 3.0))

    cmap = plt.cm.RdYlGn_r
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=0.6, aspect="auto")

    ax.set_xticks(np.arange(3))
    ax.set_yticks(np.arange(3))
    ax.set_xticklabels(col_labels, fontsize=8)
    ax.set_yticklabels(row_labels, fontsize=8)

    # Move x ticks to top
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    ax.set_xlabel("Monitor", fontsize=9, labelpad=8)
    ax.set_ylabel("Attack", fontsize=9)

    # Annotate cells
    for i in range(3):
        for j in range(3):
            val = data[i, j]
            # white text on dark cells, black on light
            text_color = "white" if val > 0.30 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=10, fontweight="bold", color=text_color)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=7)

    ax.set_title("Attack Success Rate", fontsize=10, pad=40)

    # Restore all spines for heatmap
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / "transfer_matrix.pdf")
    plt.close(fig)
    print(f"  -> {OUT / 'transfer_matrix.pdf'}")


# ---------------------------------------------------------------------------
# Figure 4: Held-out Evaluation (grouped bar)
# ---------------------------------------------------------------------------
def fig_heldout():
    groups = ["vs. Baseline", "vs. Optimized\nBlue", "vs. Aggressive"]
    safety = [1.00, 0.60, 1.00]
    attack = [0.00, 0.40, 0.00]

    x = np.arange(len(groups))
    w = 0.32

    fig, ax = plt.subplots(figsize=(COL_W, 2.4))

    bars_s = ax.bar(x - w / 2, safety, w, color=BLUE, label="Safety",
                    edgecolor="white", linewidth=0.5, zorder=3)
    bars_a = ax.bar(x + w / 2, attack, w, color=RED, label="Attack success",
                    edgecolor="white", linewidth=0.5, zorder=3)

    # Value labels on bars -- inside for tall bars, above for short ones
    for bar in list(bars_s) + list(bars_a):
        h = bar.get_height()
        if h >= 0.9:
            ax.text(bar.get_x() + bar.get_width() / 2, h - 0.04,
                    f"{h:.2f}", ha="center", va="top", fontsize=7,
                    color="white", fontweight="bold")
        elif h > 0.05:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02,
                    f"{h:.2f}", ha="center", va="bottom", fontsize=7)

    ax.axhline(0.90, ls="--", color=GRAY, lw=0.8, zorder=1)
    ax.text(1.0, 0.92, "Training safety", ha="center", va="bottom",
            fontsize=7, color=GRAY)

    ax.set_ylabel("Rate")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=8)
    ax.set_ylim(0, 1.18)
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend(loc="upper center", frameon=True, fancybox=False,
              edgecolor="#cccccc", framealpha=0.9, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "heldout_eval.pdf")
    plt.close(fig)
    print(f"  -> {OUT / 'heldout_eval.pdf'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Generating figures …")
    fig_phase1()
    fig_phase2()
    fig_coevolution()
    fig_transfer()
    fig_heldout()
    print("Done.")
