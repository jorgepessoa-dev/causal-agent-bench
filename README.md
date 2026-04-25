# causal-agent-bench

Public benchmark for **causal LLM routing** — extends [RouterBench](https://github.com/withmartian/routerbench) (405k outcomes) with causal annotations (task-type, difficulty, confounders) to support offline causal evaluation and routing comparisons.

> **Status**: Feature-complete (F3.1–F3.2 in development).
> - ✅ **Published**: NeurIPS 2026 Workshop paper + Phase 3 DR-OPE validation (arXiv 2026-04-25)
> - ✅ **Features**: Schema, loaders, 5 baselines, single-router CLI, leaderboard CLI with warmup-split, CI determinism, DR-OPE support
> - ⏳ **Next**: Real RouterBench ingestion (F2.2 license pending), metric flip to DR-OPE primary (post-real-data validation)
>
> See [`docs/RESULTS.md`](docs/RESULTS.md) for reference leaderboard, [`docs/PHASE-3-VALIDATION-REPORT.md`](docs/PHASE-3-VALIDATION-REPORT.md) for validation, [`docs/ROADMAP.md`](docs/ROADMAP.md) for what comes next.

## Quick start

```bash
git clone https://github.com/jorgepessoa-dev/causal-agent-bench && cd causal-agent-bench
pip install -e .

# Single router
python -m causal_agent_bench.cli \
    --source tests/fixtures/synthetic_router_decisions.jsonl \
    --router heuristic

# All baselines, ranked (same invocation CI uses)
python -m causal_agent_bench.leaderboard_cli \
    --source tests/fixtures/synthetic_router_decisions_large.jsonl \
    --warmup-split 250 \
    --seed 0
```

Available baselines: `random`, `heuristic`, `popularity`, `thompson`, `contextual_thompson`. Causal baseline (`causal-agent-router` via Routecast) pending F3.2 PyPI publish of `cognitiveos.core`.

`--warmup-split N` takes the first N rows of `--source` as warmup (pre-fits
learners) and evaluates on the remainder. Use `--warmup <path>` to supply a
separate warmup file instead. See [`docs/RESULTS.md`](docs/RESULTS.md) for
the reference ranking on the 500-row synthetic fixture.

## Why

Existing LLM-routing benchmarks (RouterBench, MTBench) score average performance but do not distinguish **causal effects** from observational correlations. `causal-agent-bench` adds the annotations and evaluation harness needed to compare routing policies under interventional semantics (Pearl-style) and with doubly-robust OPE.

## Intended outputs

1. **Annotated dataset** — RouterBench + causal metadata (task_type, difficulty, latent confounders).
2. **Evaluation harness** — reproducible ranking of routers under multiple metrics (cost-quality Pareto, causal regret, calibration).
3. **Public leaderboard** — GitHub Actions auto-run on PRs, results versioned by commit hash.
4. **Baselines** — random, cost-heuristic, popularity, global Thompson, stratified contextual Thompson, and (pending F3.2) a full causal baseline via Routecast.

## License

Apache-2.0 (preliminary; confirm in F2.1 finalization).

## Publication

- **Paper**: "causal-agent-bench: An Open Benchmark and Evaluation Protocol for Causal LLM Routing" (NeurIPS 2026 Workshop, arXiv 2026-04-25)
- **Validation**: [Phase 3 DR-OPE validation report](docs/PHASE-3-VALIDATION-REPORT.md) — 5-seed grid, Thompson stability σ=0.005, gate assessment
- **Gating protocol**: [Phase 4 metric flip decision](docs/PHASE-4-GATING-PROTOCOL.md) — Tier 1 PASS (synthetic), Tier 2 pending (real-data)

## Links

- **Paper & code**: [arXiv link pending]() | GitHub: [`causal-agent-bench`](https://github.com/jorgepessoa-dev/causal-agent-bench) (Apache-2.0)
- **Upstream**: [RouterBench](https://github.com/withmartian/routerbench) (MIT; dataset license TBC — see `docs/upstream_sources.md`)
- **Reference implementation**: `Routecast` (separate repo, in development)
- **Contributing**: [Submitting a router](docs/SUBMITTING.md) | [Metric definitions](docs/METRICS.md)
- **Planning**: [CognitiveOS ADR-001](https://github.com/jorgepessoa-dev/CognitiveOS/blob/main/research/plan/decisions/ADR-001-gate-f0-go.md) (design record)

## Status

- [x] Scaffold directory tree + governance files (F2.1)
- [x] Schema + DataSource Protocol + RouterBench JSONL loader (F2.2 prep)
- [x] Baselines: `RandomRouter`, `HeuristicRouter`, `PopularityRouter`, `ThompsonRouter`, `ContextualThompsonRouter` (F2.3 — ≥4 gate exceeded)
- [x] Evaluation harness + single-router CLI + combined leaderboard CLI with `--warmup-split` (F2.3–F2.4)
- [x] Leaderboard GitHub Actions workflow — one ranked JSON artifact per commit, 50/50 warmup-split on 500-row fixture (F2.4)
- [x] Submission guide, metric definitions, results reference (F2.5 — [`docs/SUBMITTING.md`](docs/SUBMITTING.md), [`docs/METRICS.md`](docs/METRICS.md), [`docs/RESULTS.md`](docs/RESULTS.md))
- [x] DR-OPE implementation: propensity estimator + reward model + formula (Phase 2, F3.1 prep)
- [x] DR-OPE validation: 5-seed synthetic grid, stability σ=0.005, gate assessment (Phase 3, F3.1 support)
- [x] Paper published + Phase 3 validation documented (F3.1, NeurIPS 2026 Workshop, arXiv 2026-04-25)
- [ ] Real RouterBench seed — license check + 5k annotated decisions (F2.2, blocked on upstream license clarification)
- [ ] Real-data validation: Tier 2 gates (κ ≥ 0.7 inter-rater, reward MAE < 0.15, propensity coverage ≥ 60%) (Phase 4, post-licensing)
- [ ] Metric flip: DR-OPE as PRIMARY (once Tier 2 gates pass, post-real-data validation)
- [ ] Causal baseline: `causal-agent-router` via Routecast (F3.2+, blocked on Routecast integration)
