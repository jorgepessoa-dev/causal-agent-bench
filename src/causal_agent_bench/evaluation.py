"""Benchmark evaluation (F2.3): run a Router over a DataSource, aggregate metrics.

The evaluation harness is deliberately thin. Each row in the DataSource
already carries the *observed* outcome (cost + quality for the upstream
chosen model). When we evaluate a candidate router, two cases arise:

1. **Match** — the candidate picks the same model the upstream log picked.
   We can use the observed outcome directly as an unbiased estimate.
2. **Mismatch** — the candidate picks a different model. We do NOT have
   an observation for that model on that prompt, so the row is excluded
   from quality/cost averaging (flagged via ``coverage`` metric).

This is the simplest IPS-friendly shape; full doubly-robust evaluation will
land once we wire causal-agent-router's SCM into scoring. For now, the
report exposes:

- ``coverage``: fraction of rows where router's pick matched the log
- ``mean_quality``: average observed_quality over matched rows
- ``mean_cost``: average observed_cost over matched rows
- ``per_difficulty``: the same three metrics bucketed by annotation.difficulty
- ``n_rows``: total rows seen
- ``n_matches``: rows where match occurred
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

from .loader import DataSource
from .router import Router
from .schema import AnnotatedDecision


@dataclass(frozen=True)
class BucketMetrics:
    n_rows: int
    n_matches: int
    mean_quality: float
    mean_cost: float

    @property
    def coverage(self) -> float:
        return self.n_matches / self.n_rows if self.n_rows else 0.0


@dataclass(frozen=True)
class EvaluationReport:
    n_rows: int
    n_matches: int
    mean_quality: float
    mean_cost: float
    per_difficulty: Dict[str, BucketMetrics] = field(default_factory=dict)

    @property
    def coverage(self) -> float:
        return self.n_matches / self.n_rows if self.n_rows else 0.0


def _aggregate(n_rows: int, qualities: list, costs: list) -> BucketMetrics:
    n_matches = len(qualities)
    mean_q = sum(qualities) / n_matches if n_matches else 0.0
    mean_c = sum(costs) / n_matches if n_matches else 0.0
    return BucketMetrics(
        n_rows=n_rows,
        n_matches=n_matches,
        mean_quality=mean_q,
        mean_cost=mean_c,
    )


def evaluate_router(router: Router, source: DataSource) -> EvaluationReport:
    """Run ``router`` over ``source``; return aggregated metrics.

    Rows where the router picks a model NOT matching the upstream log are
    counted in ``n_rows`` but excluded from quality/cost means (see module
    docstring). ``coverage`` tells you how much of the dataset is usable
    for this router under the IPS-match interpretation.
    """
    total_rows = 0
    qualities: list = []
    costs: list = []
    bucket_totals: Dict[str, int] = defaultdict(int)
    bucket_q: Dict[str, list] = defaultdict(list)
    bucket_c: Dict[str, list] = defaultdict(list)

    for ad in source:
        if not isinstance(ad, AnnotatedDecision):
            raise TypeError(
                f"DataSource must yield AnnotatedDecision; got {type(ad).__name__}"
            )
        total_rows += 1
        diff = ad.annotation.difficulty
        bucket_totals[diff] += 1
        choice = router.route(decision=ad.decision, annotation=ad.annotation)
        if choice.selected_model == ad.decision.selected_model:
            qualities.append(ad.decision.observed_quality)
            costs.append(ad.decision.observed_cost)
            bucket_q[diff].append(ad.decision.observed_quality)
            bucket_c[diff].append(ad.decision.observed_cost)

    per_difficulty = {
        diff: _aggregate(bucket_totals[diff], bucket_q[diff], bucket_c[diff])
        for diff in bucket_totals
    }

    overall = _aggregate(total_rows, qualities, costs)
    return EvaluationReport(
        n_rows=total_rows,
        n_matches=overall.n_matches,
        mean_quality=overall.mean_quality,
        mean_cost=overall.mean_cost,
        per_difficulty=per_difficulty,
    )


__all__ = ["BucketMetrics", "EvaluationReport", "evaluate_router"]
