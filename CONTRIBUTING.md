# Contributing

`causal-agent-bench` accepts contributions via pull request. The scaffold is minimal on purpose — contribution surface will harden as F2.3-F2.5 land.

## Current state

Early-alpha. 4 baselines and the leaderboard harness are committed; real RouterBench ingestion is license-blocked (see `docs/upstream_sources.md`). Open an issue before starting non-trivial work.

**Adding a new router?** Read `docs/SUBMITTING.md` — it covers the Protocol contract, determinism rules, and ranking semantics.

## Types of contribution welcomed

1. **Router implementations** — submit a new baseline in `src/causal_agent_bench/routers/` conforming to the harness interface (defined in F2.3).
2. **Dataset extensions** — additional annotations on top of the RouterBench seed (task-type, difficulty, confounders).
3. **Metric proposals** — causal evaluation metrics with precise definitions + reference implementations.
4. **Reproducibility fixes** — scripts, CI glitches, version pins.

## Ground rules

- **Reproducibility is a requirement**, not a nice-to-have. Every claim in a PR must tie to a pinned commit + deterministic seed + environment lock.
- **No hidden data**. Datasets and annotations must be redistributable under Apache-2.0-compatible terms.
- **No proprietary routers as baselines** unless wrapped in a clean interface with public reproduction instructions.

## Workflow

1. Fork, branch from `main`.
2. `pip install -e .[dev]` (or `uv pip install -e .[dev]`).
3. Write tests first (we aim for >80% coverage on new code).
4. `pytest` must pass locally.
5. Open PR with a filled-in template.

## License

Contributions are accepted under Apache-2.0 (see `LICENSE`). By opening a PR you affirm you have the right to submit the work under this license.
