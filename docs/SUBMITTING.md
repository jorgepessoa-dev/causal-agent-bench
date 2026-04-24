# Submitting a router to the leaderboard

This benchmark is early-alpha. The submission surface is deliberately narrow —
one file, one class, one PR — and will harden as the dataset and harness
stabilize.

## What a submission is

A PR against `main` that adds a new router to
`src/causal_agent_bench/routers/` (or an external package whose `Router`
conforms to the protocol in `src/causal_agent_bench/router.py`) and wires it
into the leaderboard.

## Minimum requirements

1. **Protocol conformance.** Your class implements the `Router` Protocol:

   ```python
   class Router(Protocol):
       def route(
           self,
           *,
           decision: RouterDecision,
           annotation: CausalAnnotation,
       ) -> RouterChoice: ...
   ```

2. **Deterministic under a fixed seed.** If your router uses randomness, it
   accepts a `seed` parameter and two runs with the same seed produce
   identical outputs.

3. **No network at evaluation time.** The leaderboard CI has no API keys. If
   your router needs learned weights or a calibration table, ship them in
   the repo or load from a pinned artifact.

4. **Tests.** At least one test that instantiates your router and calls
   `evaluate_router` against a fixture under `tests/fixtures/`. The test
   must pass locally without network access.

5. **License.** Your contribution is offered under Apache-2.0 (the repo
   license). If your router depends on a package under an incompatible
   license, flag it in the PR description.

## How the leaderboard ranks you

The CI job runs:

```bash
python -m causal_agent_bench.leaderboard_cli \
    --source tests/fixtures/synthetic_router_decisions_large.jsonl \
    --warmup-split 250 \
    --seed 0 \
    --output leaderboard.json
```

The first 250 rows pre-fit learning routers; the remaining 250 are evaluated.
Reference numbers: [`docs/RESULTS.md`](RESULTS.md).

`LeaderboardResult.ranked()` sorts by:

1. **`mean_quality`** (descending) — IPS-matched observed quality.
2. **`coverage`** (descending) — fraction of rows whose logged
   `selected_model` matched your router's pick (tiebreak).
3. **router name** (ascending, deterministic) — final tiebreak.

Coverage is a tiebreak, not the objective. A router that refuses to pick
anything but the logged model will score high coverage and perfect
mean_quality on that subset, but won't be useful; the dedicated F2.2
dataset will weight this appropriately once it lands.

## What is *not* in scope for a submission

- Changing the schema (`RouterDecision`, `CausalAnnotation`,
  `AnnotatedDecision`) — those are frozen baselines for F2. Open an issue
  first.
- Changing the ranking function without an ADR in the companion CognitiveOS
  repo.
- Vendoring proprietary model weights.

## Workflow

1. Open an issue describing the router and its expected positioning
   (floor baseline / learning / causal / other). Wait for a maintainer
   ack before spending real effort.
2. Fork, branch from `main`.
3. Add your router + tests. Keep the diff tight — docstrings over README
   prose, no new top-level abstractions unless justified.
4. `uv pip install -e .[dev]` then `uv run pytest -q` — must be clean.
5. `uv run ruff check .` + `uv run mypy src` — must be clean.
6. Open PR with: router name, positioning, citation if derived from
   published work, and a one-line explanation of the determinism strategy.

## Reproducibility receipt

Every PR that changes the leaderboard ranking must include in the
description:

- Commit hash your result was produced on.
- Seed used (default `0`; change only if you have a reason and explain).
- A note on whether your router's propensity is exact (e.g. `RandomRouter`:
  `1/|candidates|`), approximate, or `None` (in which case your router is
  not IPS-safe for naive off-policy estimators — that's fine, the harness
  uses match-IPS, but flag it so reviewers know).

## When in doubt

Open a draft PR early and ask. Small surface + clear determinism rules
mean the iteration loop is fast.
