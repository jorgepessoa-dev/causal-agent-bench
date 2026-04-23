# causal-agent-bench

Public benchmark for **causal LLM routing** — extends [RouterBench](https://github.com/withmartian/routerbench) (405k outcomes) with causal annotations (task-type, difficulty, confounders) to support offline causal evaluation and routing comparisons.

> **Status**: Scaffold (F2.1 — pre-dataset). Not installable yet. See `docs/ROADMAP.md`.

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
- [ ] Dataset seed (F2.2)
- [ ] Baseline implementations (F2.3)
- [ ] Leaderboard CI (F2.4)
- [ ] Contribution docs finalised (F2.5)
