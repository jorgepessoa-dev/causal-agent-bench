# Metric definitions

This doc defines every metric the leaderboard surfaces. Each definition
ties to the exact line of code that computes it so reviewers can audit.

Status: **match-IPS (interval-1)**. Full doubly-robust (DR) metrics land
once the causal baseline (Routecast) wires its SCM into scoring.

For the current baseline numbers on the synthetic fixture, see
[`RESULTS.md`](RESULTS.md).

## Notation

- `D` = dataset (sequence of `AnnotatedDecision` rows).
- For row `i`: `a_i` = logged `selected_model`, `a'_i` = router's pick,
  `q_i` ∈ [0, 1] = `observed_quality`, `c_i` ≥ 0 = `observed_cost` (USD).
- `M_i := 𝟙[a'_i == a_i]` (match indicator).
- `|M|` = `Σ M_i` = number of matched rows.

## Per-router metrics

### `n_rows`

Total rows evaluated, including mismatches.

```
n_rows = |D|
```

Source: `evaluation.py::evaluate_router` (loop counter `total_rows`).

### `n_matches`

Rows where router's pick equals the logged model.

```
n_matches = Σ_i M_i
```

Source: `evaluation.py::evaluate_router` (`qualities.append` on match branch).

### `coverage`

Fraction of rows usable under match-IPS.

```
coverage = n_matches / n_rows   (0 if n_rows == 0)
```

Source: `BucketMetrics.coverage` property.

### `mean_quality`

Average observed quality over matched rows only.

```
mean_quality = (1 / |M|) · Σ_i M_i · q_i        (0 if |M| == 0)
```

**Interpretation.** If `a'_i ≠ a_i`, we have no outcome for `a'_i` on prompt
`i` in the log — we can't plug in a value. Match-IPS resolves this by
dropping those rows from the numerator AND denominator of the mean. The
remaining estimate is unbiased for `E[q | router agrees with log]`, not for
`E[q | router's policy]`. See §Caveats.

Source: `evaluation.py::_aggregate`.

### `mean_cost`

Average observed cost over matched rows only. Same formula as
`mean_quality` with `c_i` substituted for `q_i`. Same caveats.

### `per_difficulty`

The four metrics above, bucketed by `annotation.difficulty`. Buckets are
formed from whatever difficulty levels appear in the dataset (no fixed
enum). A bucket with zero matches reports `mean_quality = mean_cost = 0`
and `coverage = 0` — flagged by a `n_matches = 0` reading.

Source: `evaluation.py::evaluate_router` (`bucket_q`, `bucket_c`).

## Leaderboard ranking

Applied in `leaderboard.py::LeaderboardResult.ranked`:

```python
sorted_by(
    key=(−mean_quality, −coverage, router_name_ascending)
)
```

1. **Primary**: higher `mean_quality` wins.
2. **Tiebreak 1**: higher `coverage`. (Defends against the trivial
   "always agree with the log" router that inflates `mean_quality` over
   a narrow sliver.)
3. **Tiebreak 2**: router name, ascending. Ensures deterministic output
   when two routers are genuinely equal.

## Caveats (read before trusting the ranking)

1. **Match-IPS is not policy evaluation.** The current metrics estimate
   "how well does the router do on the subset of rows it happens to agree
   with the log on", not the expected reward under the router's policy.
   A router with 5% coverage and `mean_quality = 0.95` may be useless in
   practice if it never picks anything else.
2. **No propensity weighting.** `RandomRouter` reports a true propensity
   (`1/|candidates|`), `HeuristicRouter` is deterministic (propensity 1 on
   its pick, 0 elsewhere — unsafe for IPS), and `ThompsonRouter` /
   `PopularityRouter` mark propensity `None`. Once the dataset is large
   enough, we'll add weighted estimators; until then, coverage is the only
   honest comparison dimension after quality.
3. **Cost is not optimized.** Cost is reported per router but not folded
   into the ranking. F2.3 completion + causal baseline will add
   cost-weighted Pareto ranking.
4. **Quality scale is dataset-dependent.** `observed_quality` ∈ [0, 1],
   but the underlying semantics (accuracy, win rate, judge score) are
   defined by upstream. `causal-agent-bench` does not re-score prompts.
5. **Ties are common on small fixtures.** On the 3-row synthetic
   fixture, multiple routers often post identical `mean_quality`; the
   deterministic tiebreak by name makes the CI output stable but is not
   meaningful.

## Roadmap (metrics, not infrastructure)

- **DR-OPE** via Routecast's SCM. Required before claiming anything about
  policy value.
- **Cost-weighted Pareto frontier**. Tracked as an additional ranking,
  not a replacement.
- **Calibration metrics** (ECE, Brier) once routers start emitting
  confidence on their picks.
- **Causal regret** (intervention-vs-observation gap) once annotations
  include counterfactual estimates.

These are scoped for F3 (paper). They do not change the F2 leaderboard's
current contract.
