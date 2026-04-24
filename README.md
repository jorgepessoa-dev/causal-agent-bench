# causal-agent-bench

Public benchmark for **causal LLM routing** — extends [RouterBench](https://github.com/withmartian/routerbench) (405k outcomes) with causal annotations (task-type, difficulty, confounders) to support offline causal evaluation and routing comparisons.

> **Status**: Early-alpha. Schema, loaders, baselines, and evaluation harness landed (F2.1–F2.4 scaffolds). Real RouterBench ingestion pending F2.2 dedicated session. See `docs/ROADMAP.md`.

## Quick start

```bash
git clone https://github.com/jorgepessoa-dev/causal-agent-bench && cd causal-agent-bench
pip install -e .
python -m causal_agent_bench.cli \
    --source tests/fixtures/synthetic_router_decisions.jsonl \
    --router heuristic
```

Available baselines: `random`, `heuristic`. Smarter routers (RouteLLM reimpl, causal-agent-router) are scoped for the next commits.

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

- Upstream: [RouterBench](https://github.com/withmartian/routerbench)
- Reference routing library (causal): `Routecast` (separate repo, in development)
- Planning record: [CognitiveOS research/plan/decisions/ADR-001](https://github.com/jorgepessoa-dev/CognitiveOS/blob/main/research/plan/decisions/ADR-001-gate-f0-go.md)

## Status

- [x] Scaffold directory tree + governance files
- [x] Schema + DataSource Protocol (F2.1, F2.2 prep)
- [x] RouterBench JSONL loader (F2.2 prep; real ingestion pending license check)
- [x] Baselines: `RandomRouter`, `HeuristicRouter` (F2.3 — 2 of 4; RouteLLM + causal pending)
- [x] Evaluation harness + CLI (F2.3 + F2.4 scaffold)
- [x] Leaderboard workflow (F2.4 scaffold — runs on every PR)
- [ ] Real RouterBench seed (F2.2)
- [ ] Full baselines set: RouteLLM-reimpl + causal-agent-router (F2.3 completion)
- [ ] Contribution docs finalised (F2.5)
