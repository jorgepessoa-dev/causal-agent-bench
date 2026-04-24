# Reference leaderboard — synthetic fixture

This page records the reference baseline ranking on the repo's synthetic
fixture. New routers should compare against these numbers on the same
source + seed before submitting.

## Source & command

```bash
python -m causal_agent_bench.leaderboard_cli \
    --source tests/fixtures/synthetic_router_decisions_large.jsonl \
    --warmup-split 250 \
    --seed 0 \
    --output leaderboard.json
```

- **Source**: `tests/fixtures/synthetic_router_decisions_large.jsonl` (500 rows, seed-0 via `scripts/generate_synthetic_fixture.py`)
- **Split**: first 250 rows → warmup, remaining 250 → eval
- **Seed**: `0` for stochastic routers
- **Evaluation**: match-IPS (only rows where the router's pick equals the logged pick contribute to `mean_quality`)

## Reference ranking (commit `aadef4a`)

| Rank | Router                 | mean_quality | coverage | mean_cost   | n_matches |
|-----:|------------------------|-------------:|---------:|------------:|----------:|
|    1 | `thompson`             |       0.8247 |    0.384 |   0.011502  |        96 |
|    2 | `heuristic`            |       0.8154 |    0.576 |   0.008783  |       144 |
|    3 | `contextual_thompson`  |       0.8071 |    0.404 |   0.008535  |       101 |
|    4 | `popularity`           |       0.7921 |    0.360 |   0.007378  |        90 |
|    5 | `random`               |       0.7736 |    0.388 |   0.005722  |        97 |

Ranking key: `mean_quality` desc → `coverage` desc → name asc (see [`METRICS.md`](METRICS.md)).

## Notes on these numbers

- **`thompson` wins on this fixture** because the 500-row synthetic cost/quality
  structure has stable model-per-task signal; global pooling converges faster
  than per-stratum.
- **`contextual_thompson` pays for stratification**. With 250 warmup rows spread
  across 6 task-types × 5 difficulties × up-to-4 candidates per row, most
  buckets see <3 samples. This is the bias-variance trade-off surfacing;
  contextual should overtake flat once per-stratum sample count passes ~10.
- **`heuristic` has the highest coverage** by design — it always picks the
  cheapest candidate, which matches the logged router often on `trivial`/`easy`
  rows where the upstream picks cheap models.
- **`popularity` beats `random` only slightly on quality** (0.79 vs 0.77).
  Popularity conditions on task_type but ignores difficulty, so it suffers the
  same Simpson's-paradox concerns the contextual variant exists to address.

## Reproducing

Determinism: same `--source`, same `--seed`, same `--warmup-split` ⇒
byte-identical `leaderboard.json`. Assert this in your test matrix:

```bash
python -m causal_agent_bench.leaderboard_cli \
    --source tests/fixtures/synthetic_router_decisions_large.jsonl \
    --warmup-split 250 --seed 0 --output /tmp/a.json
python -m causal_agent_bench.leaderboard_cli \
    --source tests/fixtures/synthetic_router_decisions_large.jsonl \
    --warmup-split 250 --seed 0 --output /tmp/b.json
diff /tmp/a.json /tmp/b.json  # must be empty
```

## When this page changes

Any commit that changes the ranking on the default fixture must update the
table above. CI uploads `leaderboard-<sha>.json` as an artifact; compare it
against these numbers before merging.

Once real RouterBench data lands (F2.2), a second reference table will be
added under a **Real data** section here — synthetic numbers will remain
as the deterministic smoke ranking.
