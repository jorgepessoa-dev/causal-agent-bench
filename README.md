# causal-agent-bench

Public benchmark for **causal LLM routing** — extends [RouterBench](https://github.com/withmartian/routerbench) (405k outcomes) with causal annotations (task-type, difficulty, confounders) to support offline causal evaluation and routing comparisons.

> **Status**: Early-alpha. Schema, loaders, 5 baselines, single-router CLI, combined leaderboard CLI with warmup-split, and CI workflow all landed (F2.1–F2.5). Real RouterBench ingestion pending F2.2 license resolution. See [`docs/RESULTS.md`](docs/RESULTS.md) for the current leaderboard and [`docs/ROADMAP.md`](docs/ROADMAP.md) for what comes next.

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

## Links

- Upstream: [RouterBench](https://github.com/withmartian/routerbench) (MIT; dataset license TBC — see `docs/upstream_sources.md`)
- Reference routing library (causal): `Routecast` (separate repo, in development)
- Submitting a router: [`docs/SUBMITTING.md`](docs/SUBMITTING.md)
- Metric definitions: [`docs/METRICS.md`](docs/METRICS.md)
- Planning record: [CognitiveOS research/plan/decisions/ADR-001](https://github.com/jorgepessoa-dev/CognitiveOS/blob/main/research/plan/decisions/ADR-001-gate-f0-go.md)

## Status

- [x] Scaffold directory tree + governance files (F2.1)
- [x] Schema + DataSource Protocol + RouterBench JSONL loader (F2.2 prep)
- [x] Baselines: `RandomRouter`, `HeuristicRouter`, `PopularityRouter`, `ThompsonRouter`, `ContextualThompsonRouter` (F2.3 — ≥4 gate exceeded)
- [x] Evaluation harness + single-router CLI + combined leaderboard CLI with `--warmup-split` (F2.3–F2.4)
- [x] Leaderboard GitHub Actions workflow — one ranked JSON artifact per commit, 50/50 warmup-split on 500-row fixture (F2.4)
- [x] Submission guide, metric definitions, results reference (F2.5 — [`docs/SUBMITTING.md`](docs/SUBMITTING.md), [`docs/METRICS.md`](docs/METRICS.md), [`docs/RESULTS.md`](docs/RESULTS.md))
- [ ] Real RouterBench seed — license check + 5k annotated decisions (F2.2 dedicated session, blocked on upstream license clarification)
- [ ] Causal baseline: `causal-agent-router` via Routecast (F2.3 extension, blocked on F3.2 PyPI publish)
