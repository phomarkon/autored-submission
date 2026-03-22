"""Held-out evaluation: best red vs best blue + baselines on unseen tasks."""

import json
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("heldout")

PROJECT_DIR = Path(__file__).parent
RESULTS_DIR = PROJECT_DIR / "results"

# Load env
env_file = PROJECT_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

from board import load_board
from eval import evaluate
from models import OllamaModel, DEFAULT_UNTRUSTED, DEFAULT_TRUSTED
from tasks import HELDOUT_TASKS, _assign_backdoor_triggers

import random


def run_heldout():
    board = load_board()
    p1 = board["phase_results"]["1"]
    p2 = board["phase_results"]["2"]

    # Prepare held-out tasks
    tasks = _assign_backdoor_triggers([{**t} for t in HELDOUT_TASKS])
    logger.info("Held-out tasks: %d", len(tasks))

    untrusted = OllamaModel(DEFAULT_UNTRUSTED, temperature=0.7, endpoint="auto")
    trusted = OllamaModel(DEFAULT_TRUSTED, temperature=0.3, endpoint="auto")

    # Configs to evaluate
    configs = {
        "best_red_vs_baseline": {
            "red": p1.get("best_attack_code"),
            "blue": (PROJECT_DIR / "baselines" / "trusted_monitoring.py").read_text(),
        },
        "best_red_vs_best_blue": {
            "red": p1.get("best_attack_code"),
            "blue": p2.get("best_blue_code"),
        },
        "best_red_vs_aggressive": {
            "red": p1.get("best_attack_code"),
            "blue": (PROJECT_DIR / "baselines" / "trusted_monitoring_with_defer.py").read_text(),
        },
    }

    results = {}
    for name, cfg in configs.items():
        logger.info("Evaluating: %s", name)

        # Write configs to disk
        if cfg["red"]:
            Path(PROJECT_DIR / "red_attack.py").write_text(cfg["red"])
        Path(PROJECT_DIR / "blue_protocol.py").write_text(cfg["blue"])

        try:
            # Monkey-patch sample_tasks to use held-out tasks
            import tasks as tasks_mod
            orig_sample = tasks_mod.sample_tasks

            def heldout_sample(n, seed=None):
                rng = random.Random(seed)
                return rng.sample(tasks, min(n, len(tasks)))

            tasks_mod.sample_tasks = heldout_sample

            r = evaluate(
                mode="both", n_tasks=len(tasks),
                round_num=9999, untrusted=untrusted, trusted=trusted,
            )

            tasks_mod.sample_tasks = orig_sample

            entry = {
                "safety": r["safety"],
                "usefulness": r["usefulness"],
                "attack_success": r["attack_success"],
                "auroc": r.get("auroc", 0.5),
                "deferral_rate": r.get("deferral_rate", 0),
                "fpr": r.get("fpr", 0),
                "fnr": r.get("fnr", 0),
                "backdoor_insert_rate": r.get("backdoor_insert_rate", 0),
            }
            results[name] = entry
            logger.info("%s: S=%.2f U=%.2f A=%.2f", name, entry["safety"], entry["usefulness"], entry["attack_success"])

            # Save individual result
            with open(RESULTS_DIR / f"heldout_{name}.json", "w") as f:
                json.dump({**entry, "details": r.get("details", [])}, f, indent=2)

        except Exception as e:
            logger.error("%s failed: %s", name, e, exc_info=True)

    # Save summary
    with open(RESULTS_DIR / "heldout_summary.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n=== HELD-OUT EVALUATION ===")
    print(f"{'Config':<30} {'Safety':>8} {'Useful':>8} {'Attack':>8}")
    for name, r in results.items():
        print(f"{name:<30} {r['safety']:>8.2f} {r['usefulness']:>8.2f} {r['attack_success']:>8.2f}")


if __name__ == "__main__":
    run_heldout()
