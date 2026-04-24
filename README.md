# causal-agent-bench

Public benchmark for **causal LLM routing** — extends [RouterBench](https://github.com/withmartian/routerbench) (405k outcomes) with causal annotations (task-type, difficulty, confounders) to support offline causal evaluation and routing comparisons.

> **Status**: Early-alpha. Schema, loaders, 4 baselines, single-router CLI, combined leaderboard CLI, and CI workflow all landed (F2.1–F2.4). Real RouterBench ingestion pending F2.2 dedicated session. See `docs/ROADMAP.md`.

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
    --source tests/fixtures/synthetic_router_decisions.jsonl \
    --seed 0
```

Available baselines: `random`, `heuristic`, `popularity`, `thompson`. Causal baseline (`causal-agent-router` via Routecast) pending F3.2 PyPI publish of `cognitiveos.core`.

## Why

Existing LLM-routing benchmarks (RouterBench, MTBench) score average performance but do not distinguish **causal effects** from observational correlations. `causal-agent-bench` adds the annotations and evaluation harness needed to compare routing policies under interventional semantics (Pearl-style) and with doubly-robust OPE.

## Intended outputs

1. **Annotated dataset** — RouterBench + causal metadata (task_type, difficulty, latent confounders).
2. **Evaluation harness** — reproducible ranking of routers under multiple metrics (cost-quality Pareto, causal regret, calibration).
3. **Public leaderboard** — GitHub Actions auto-run on PRs, results versioned by commit hash.
4. **Baselines** — random, cost-heuristic, RouteLLM-reimpl, and a causal baseline (reference implementation).

## License

Apache-2.0 (preliminary; confirm in F2.1 finalization).

## Links

- Upstream: [RouterBench](https://github.com/withmartian/routerbench) (MIT; dataset license TBC — see `docs/upstream_sources.md`)
- Reference routing library (causal): `Routecast` (separate repo, in development)
- Submitting a router: [`docs/SUBMITTING.md`](docs/SUBMITTING.md)
- Planning record: [CognitiveOS research/plan/decisions/ADR-001](https://github.com/jorgepessoa-dev/CognitiveOS/blob/main/research/plan/decisions/ADR-001-gate-f0-go.md)

## Status

- [x] Scaffold directory tree + governance files (F2.1)
- [x] Schema + DataSource Protocol + RouterBench JSONL loader (F2.2 prep)
- [x] Baselines: `RandomRouter`, `HeuristicRouter`, `PopularityRouter`, `ThompsonRouter` (F2.3 — ≥4 gate met)
- [x] Evaluation harness + single-router CLI + combined leaderboard CLI (F2.3–F2.4)
- [x] Leaderboard GitHub Actions workflow — one ranked JSON artifact per commit (F2.4)
- [ ] Real RouterBench seed — license check + 5k annotated decisions (F2.2 dedicated session)
- [ ] Causal baseline: `causal-agent-router` via Routecast (F2.3 completion, blocked on F3.2 PyPI publish)
- [ ] Contribution docs deepened + submission guide (F2.5)
