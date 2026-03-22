# AutoRed: Measuring the Elicitation Gap via Automated Red-Blue Optimization

**AI Control Hackathon 2026 — Apart Research x Redwood Research**

> Automated optimization can partially close the elicitation gap, but the improvements are brittle. Optimized strategies overfit to their training opponents. The best optimized monitor drops from 90% safety during training to 47% on held-out tasks, while a simple threshold baseline maintains 100%.

## Quick Start

```bash
./run_demo.sh          # auto-detects Docker, uv, or pip
# Then open http://localhost:8501
```

Or explicitly with Docker:

```bash
docker build -t autored-demo .
docker run --rm -p 8501:8501 autored-demo
```

## What is this?

AutoRed automates both red team attack optimization and blue team monitor optimization in a code backdoor detection setting adapted from the [AI Control framework](https://arxiv.org/abs/2312.06942) (Greenblatt et al., 2024).

A reasoning model iteratively improves strategies on each side across five phases:

| Phase | What happens | Key result |
|-------|-------------|------------|
| **0. Baselines** | 3 fixed monitors vs. naive attacks | Baseline catches 100% of naive attacks |
| **1. Red optimization** | 15 iterations optimizing attack against fixed monitor | Attack success: 0% → 30% |
| **2. Blue optimization** | 15 iterations optimizing monitor against best attack | Safety 90%, usefulness 90% |
| **3. Co-evolution** | 5 rounds alternating red/blue (3 iters each) | Oscillatory dynamics, peak attack 60% |
| **4. Transfer test** | 3×3 attack-monitor matrix + held-out evaluation | **Optimized monitor fails: 47% safety on held-out** |

## Central Finding

The optimized monitor achieves 90% safety during training but **47% on held-out tasks** (3 seeds, ±0.09). Its AUROC drops to 0.50 (chance). A simple threshold baseline maintains **100% safety with zero variance**.

Why? The optimizer learns pattern-specific AST rules (hashlib imports, hex strings) that don't fire on unseen code. The overfitted prompt inverts suspicion scoring on out-of-distribution inputs.

## Luthien Proxy Integration

AutoRed's findings translate directly to [Luthien Proxy](https://github.com/LuthienResearch/luthien-proxy) deployment decisions. We provide two Luthien-compatible policy classes:

| Policy | Held-out Safety | AUROC | Deploy? |
|--------|----------------|-------|---------|
| `baseline_monitor` | 80% | 0.85 | Yes |
| `optimized_monitor` | 47% | 0.50 | **No** — overfits to hash-based attacks |

```bash
# Deploy the robust baseline via Luthien
cp luthien_policies/baseline_monitor.yaml ~/.luthien/policy.yaml
luthien up
```

The optimized monitor is included as a **cautionary example** — it demonstrates what happens when you deploy an optimized policy without held-out validation.

## Repository Structure

```
├── demo.py                  # Interactive Streamlit demo
├── run_demo.sh              # One-command demo launcher
├── run.py                   # Main pipeline (Phases 0-4)
├── eval.py                  # Evaluation harness
├── heldout_eval.py          # Held-out evaluation with multi-seed
├── tasks.py                 # Task definitions (15 training + 10 held-out)
├── models.py                # Model API wrappers (Ollama cloud)
├── board.py                 # Results board tracking
├── board.json               # All phase results
├── blue_protocol.py         # Current blue strategy
├── red_attack.py            # Current red strategy
├── plot_paper.py            # Paper figure generation
├── results/                 # All evaluation results (JSON)
│   ├── phase1_iter*.json    # Red optimization iterations
│   ├── phase2_iter*.json    # Blue optimization iterations
│   ├── phase4_*.json        # Transfer matrix results
│   ├── heldout_*.json       # Held-out evaluation results
│   └── optimizer_logs/      # Optimizer chain-of-thought logs
├── manuscript/              # Paper (NeurIPS template)
│   ├── autored_2026.tex
│   ├── autored_2026.pdf
│   ├── figures/
│   └── supplementary/       # Best red/blue strategy code
├── baselines/               # Fixed baseline strategies
└── luthien_policies/        # Luthien Proxy integration
    ├── baseline_monitor.py  # Robust, pattern-agnostic (DEPLOY THIS)
    ├── optimized_monitor.py # Overfitted cautionary example
    ├── baseline_monitor.yaml
    └── optimized_monitor.yaml
```

## Models

| Role | Model | Purpose |
|------|-------|---------|
| U (untrusted coder) | `minimax-m2.7` | Generates code, may inject backdoors |
| T (trusted monitor) | `nemotron-3-super` (120B MoE) | Scores code suspicion |
| O (optimizer) | `deepseek-v3.1:671b` | Generates improved strategies via chain-of-thought |

## Reproducing

The full pipeline runs in ~8 hours with ~1,200 API calls at ~$50 total cost.

```bash
# Setup
./setup.sh

# Run full pipeline
python3 run.py

# Run held-out evaluation
python3 heldout_eval.py

# Generate paper figures
python3 plot_paper.py
```

## Paper

The manuscript is in `manuscript/autored_2026.pdf`. Key figures:

- **Figure 2**: Elicitation curves showing red/blue optimization over 15 iterations
- **Figure 3**: Co-evolutionary oscillatory dynamics across 5 rounds
- **Figure 4**: Transfer matrix heatmap revealing monitor overfitting
- **Figure 6**: Suspicion score inversion on held-out tasks (the "aha" figure)

## License

MIT
