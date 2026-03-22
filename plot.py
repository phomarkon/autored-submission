"""Generate figures from results."""

import json
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger("autored.plot")

PROJECT_DIR = Path(__file__).parent
FIGURES_DIR = PROJECT_DIR / "manuscript" / "figures"
FIGURES_DIR.mkdir(exist_ok=True)


def load_board():
    board_file = PROJECT_DIR / "board.json"
    if board_file.exists():
        with open(board_file) as f:
            return json.load(f)
    return None


def plot_arms_race(board: dict):
    """Phase 3 co-evolution: safety + attack success over rounds."""
    p3 = board.get("phase_results", {}).get("3", {})
    rounds_data = p3.get("rounds", [])

    # Also support legacy rounds
    legacy_rounds = board.get("rounds", [])

    if not rounds_data and not legacy_rounds:
        return

    if rounds_data:
        # Phase 3 data
        x = list(range(len(rounds_data)))
        # Extract best attack/safety from each round
        attack_vals = []
        safety_vals = []
        for rd in rounds_data:
            red_iters = rd.get("red_iters", [])
            blue_iters = rd.get("blue_iters", [])
            best_a = max((ri.get("attack_success", 0) for ri in red_iters), default=0)
            best_s = max((bi.get("safety", 0) for bi in blue_iters), default=0)
            attack_vals.append(best_a)
            safety_vals.append(best_s)

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(x, safety_vals, "b-o", label="Safety (Blue best)", markersize=5, alpha=0.8)
        ax1.plot(x, attack_vals, "r-^", label="Attack Success (Red best)", markersize=5, alpha=0.8)
        ax1.set_xlabel("Co-evolution Round")
        ax1.set_ylabel("Rate")
        ax1.set_ylim(-0.05, 1.05)
        ax1.legend(loc="best")
        ax1.set_title("Phase 3: Co-evolution Arms Race")
        ax1.grid(True, alpha=0.3)
    else:
        # Legacy format
        x = [r["round"] for r in legacy_rounds]
        safety = [r["safety"] for r in legacy_rounds]
        attack = [r["attack_success"] for r in legacy_rounds]
        usefulness = [r["usefulness"] for r in legacy_rounds]

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(x, safety, "b-o", label="Safety", markersize=3, alpha=0.8)
        ax1.plot(x, usefulness, "g-s", label="Usefulness", markersize=3, alpha=0.8)
        ax1.plot(x, attack, "r-^", label="Attack Success", markersize=3, alpha=0.8)
        ax1.set_xlabel("Round")
        ax1.set_ylabel("Rate")
        ax1.set_ylim(-0.05, 1.05)
        ax1.legend(loc="best")
        ax1.set_title("Arms Race")
        ax1.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "arms_race.png", dpi=150)
    plt.close()


def _load_baseline_metrics(name: str) -> dict | None:
    """Load baseline result file if it exists."""
    path = PROJECT_DIR / "results" / f"baseline_{name}.json"
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return None


def plot_elicitation_curves(board: dict):
    """Fig 1: Elicitation curves — Left=red optimization, Right=blue optimization."""
    pr = board.get("phase_results", {})
    p1 = pr.get("1", {})
    p2 = pr.get("2", {})

    p1_iters = p1.get("iterations", [])
    p2_iters = p2.get("iterations", [])

    if not p1_iters and not p2_iters:
        return

    # Load baseline for reference lines
    baseline = _load_baseline_metrics("trusted_monitoring")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Red elicitation curve (Phase 1)
    if p1_iters:
        x1 = [it.get("iteration", i) for i, it in enumerate(p1_iters)]
        y1 = [it.get("attack_success", 0) for it in p1_iters]
        kept1 = [it.get("kept", False) for it in p1_iters]

        ax1.plot(x1, y1, "r-o", markersize=4, alpha=0.6, label="All attempts")
        # Highlight kept iterations
        kept_x = [x for x, k in zip(x1, kept1) if k]
        kept_y = [y for y, k in zip(y1, kept1) if k]
        if kept_x:
            ax1.scatter(kept_x, kept_y, color="red", s=80, zorder=5, marker="*", label="Kept improvements")
        # Running best line
        running_best = []
        best_so_far = 0
        for y in y1:
            best_so_far = max(best_so_far, y)
            running_best.append(best_so_far)
        ax1.plot(x1, running_best, "r--", alpha=0.4, label="Running best")

    if baseline:
        ax1.axhline(y=baseline.get("attack_success", 0), color="gray", linestyle="--", alpha=0.6, label="Baseline attack_success")

    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Attack Success Rate")
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_title("Phase 1: Red Elicitation Curve")
    ax1.legend(loc="best")
    ax1.grid(True, alpha=0.3)

    # Right: Blue elicitation curve (Phase 2)
    if p2_iters:
        x2 = [it.get("iteration", i) for i, it in enumerate(p2_iters)]
        y2_safety = [it.get("safety", 0) for it in p2_iters]
        y2_auroc = [it.get("auroc", 0.5) for it in p2_iters]
        kept2 = [it.get("kept", False) for it in p2_iters]

        ax2.plot(x2, y2_safety, "b-o", markersize=4, alpha=0.6, label="Safety (all)")
        ax2.plot(x2, y2_auroc, "c-s", markersize=3, alpha=0.5, label="AUROC (all)")
        kept_x = [x for x, k in zip(x2, kept2) if k]
        kept_y = [y for y, k in zip(y2_safety, kept2) if k]
        if kept_x:
            ax2.scatter(kept_x, kept_y, color="blue", s=80, zorder=5, marker="*", label="Kept improvements")

    if baseline:
        ax2.axhline(y=baseline.get("safety", 0), color="gray", linestyle="--", alpha=0.6, label="Baseline safety")

    ax2.set_xlabel("Iteration")
    ax2.set_ylabel("Rate")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title("Phase 2: Blue Elicitation Curve")
    ax2.legend(loc="best")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "elicitation_curves.png", dpi=150)
    plt.close()


def plot_asymmetry(board: dict):
    """Fig 2: Bar chart — red vs blue improvement over baseline."""
    pr = board.get("phase_results", {})
    p1 = pr.get("1", {})
    p2 = pr.get("2", {})

    p1_iters = p1.get("iterations", [])
    p2_iters = p2.get("iterations", [])

    if not p1_iters and not p2_iters:
        return

    # Compute improvements
    red_baseline = p1_iters[0].get("attack_success", 0) if p1_iters else 0
    red_best = p1.get("best_attack_success", red_baseline)
    red_improvement = red_best - red_baseline

    blue_baseline_safety = p2_iters[0].get("safety", 0) if p2_iters else 0
    blue_best_safety = p2.get("best_safety", blue_baseline_safety)
    blue_improvement = blue_best_safety - blue_baseline_safety

    fig, ax = plt.subplots(figsize=(8, 6))
    categories = ["Red (Attack\nSuccess)", "Blue (Safety)"]
    improvements = [red_improvement, blue_improvement]
    colors = ["#d62728", "#1f77b4"]

    bars = ax.bar(categories, improvements, color=colors, alpha=0.8, width=0.5)

    # Add value labels on bars
    for bar, val in zip(bars, improvements):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"+{val:.2f}", ha="center", va="bottom", fontweight="bold")

    ax.set_ylabel("Improvement Over Baseline")
    ax.set_title("Elicitation Gap: Red vs Blue Optimization Asymmetry")
    ax.grid(True, alpha=0.3, axis="y")
    ax.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "asymmetry.png", dpi=150)
    plt.close()


def plot_transfer_matrix(board: dict):
    """Fig 4: 3×3 heatmap of transfer test results."""
    p4 = board.get("phase_results", {}).get("4", {})
    matrix = p4.get("transfer_matrix", {})

    if not matrix:
        return

    attack_names = ["naive", "phase1_best", "phase3_best"]
    monitor_names = ["baseline", "phase2_best", "aggressive_defer"]

    # Build matrix
    data = np.zeros((3, 3))
    for i, atk in enumerate(attack_names):
        for j, mon in enumerate(monitor_names):
            key = f"{atk}_vs_{mon}"
            cell = matrix.get(key, {})
            data[i, j] = cell.get("attack_success", 0)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(data, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")

    # Labels
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Baseline\nMonitor", "Phase 2\nBest", "Aggressive\nDefer"], fontsize=9)
    ax.set_yticks(range(3))
    ax.set_yticklabels(["Naive\nAttack", "Phase 1\nBest", "Phase 3\nBest"], fontsize=9)
    ax.set_xlabel("Monitor")
    ax.set_ylabel("Attack")
    ax.set_title("Phase 4: Transfer Test Matrix (Attack Success Rate)")

    # Annotate cells
    for i in range(3):
        for j in range(3):
            val = data[i, j]
            color = "white" if val > 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontweight="bold")

    plt.colorbar(im, label="Attack Success Rate")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "transfer_matrix.png", dpi=150)
    plt.close()


def plot_pareto(board: dict):
    """Safety vs usefulness Pareto frontier."""
    rounds = board.get("rounds", [])
    if not rounds:
        return

    safety = [r["safety"] for r in rounds]
    usefulness = [r["usefulness"] for r in rounds]

    fig, ax = plt.subplots(figsize=(8, 8))
    scatter = ax.scatter(usefulness, safety, c=range(len(rounds)), cmap="viridis", alpha=0.7, s=30)
    plt.colorbar(scatter, label="Round")

    ax.set_xlabel("Usefulness")
    ax.set_ylabel("Safety")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Safety vs Usefulness Pareto Frontier")
    ax.grid(True, alpha=0.3)

    best = board.get("best_blue", {})
    if best.get("round", 0) > 0:
        ax.scatter(
            [best["usefulness"]], [best["safety"]],
            color="red", s=200, marker="*", zorder=5, label=f"Best (R{best['round']})"
        )
        ax.legend()

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pareto.png", dpi=150)
    plt.close()


def plot_suspicion_distribution(board: dict):
    """Suspicion score distributions (from round results)."""
    results_dir = PROJECT_DIR / "results"
    if not results_dir.exists():
        return

    honest_scores = []
    attack_scores = []

    for f in sorted(results_dir.glob("*.json"))[-10:]:  # Last 10 result files
        try:
            data = json.load(open(f))
            for d in data.get("details", []):
                meta = d.get("metadata", {})
                score = meta.get("suspicion_score") or meta.get("suspicion")
                if score is not None:
                    if d.get("mode") == "honest":
                        honest_scores.append(score)
                    else:
                        attack_scores.append(score)
        except Exception:
            continue

    if not honest_scores and not attack_scores:
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    bins = np.linspace(0, 1, 21)

    if honest_scores:
        ax.hist(honest_scores, bins=bins, alpha=0.6, label="Honest", color="green")
    if attack_scores:
        ax.hist(attack_scores, bins=bins, alpha=0.6, label="Attack", color="red")

    ax.set_xlabel("Suspicion Score")
    ax.set_ylabel("Count")
    ax.set_title("Suspicion Score Distribution")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "suspicion_dist.png", dpi=150)
    plt.close()


def plot_deferral_rate(board: dict):
    """Plot deferral rate over iterations for Phase 1 and Phase 2."""
    results_dir = PROJECT_DIR / "results"
    if not results_dir.exists():
        return

    phases = {"Phase 1": "phase1_iter", "Phase 2": "phase2_iter"}
    has_data = False

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {"Phase 1": "red", "Phase 2": "blue"}

    for label, prefix in phases.items():
        files = sorted(results_dir.glob(f"{prefix}*.json"))
        if not files:
            continue
        iters = []
        rates = []
        for f in files:
            try:
                data = json.load(open(f))
                rate = data.get("deferral_rate")
                if rate is None:
                    details = data.get("details", [])
                    n_deferred = sum(1 for d in details if d.get("decision") == "DEFER")
                    rate = n_deferred / max(len(details), 1)
                iters.append(len(iters))
                rates.append(rate)
            except Exception:
                continue
        if iters:
            ax.plot(iters, rates, f"-o", color=colors[label], markersize=4, alpha=0.7, label=label)
            has_data = True

    if not has_data:
        plt.close()
        return

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Deferral Rate")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Deferral Rate Over Iterations")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "deferral_rate.png", dpi=150)
    plt.close()


def main():
    board = load_board()
    if board is None:
        logger.warning("No board.json found")
        return

    plot_elicitation_curves(board)
    plot_asymmetry(board)
    plot_arms_race(board)
    plot_transfer_matrix(board)
    plot_pareto(board)
    plot_suspicion_distribution(board)
    plot_deferral_rate(board)
    logger.info("Plots saved to %s", FIGURES_DIR)


if __name__ == "__main__":
    main()
