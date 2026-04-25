"""Benchmark evaluation (F2.3+): run a Router over a DataSource, aggregate metrics.

The evaluation harness is deliberately thin. Each row in the DataSource
already carries the *observed* outcome (cost + quality for the upstream
chosen model). When we evaluate a candidate router, two cases arise:

1. **Match** — the candidate picks the same model the upstream log picked.
   We can use the observed outcome directly as an unbiased estimate.
2. **Mismatch** — the candidate picks a different model. We do NOT have
   an observation for that model on that prompt, so the row is excluded
   from quality/cost averaging (flagged via ``coverage`` metric).

Primary metric (F3.1): **match-IPS** (simple, unbiased under stable matches).
Secondary metric (Phase 1 validation): **DR-OPE** (doubly-robust, requires
propensity + reward model estimators; see dr_ope.py).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .loader import DataSource
from .reward_model import RewardModel
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
    # Optional DR-OPE metrics (computed if use_dr_ope=True)
    dr_quality: Optional[float] = None
    dr_cost: Optional[float] = None
    per_difficulty_dr: Optional[Dict[str, Dict[str, float]]] = None

    @property
    def coverage(self) -> float:
        return self.n_matches / self.n_rows if self.n_rows else 0.0


def _aggregate(n_rows: int, qualities: List[float], costs: List[float]) -> BucketMetrics:
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
    qualities: List[float] = []
    costs: List[float] = []
    bucket_totals: Dict[str, int] = defaultdict(int)
    bucket_q: Dict[str, List[float]] = defaultdict(list)
    bucket_c: Dict[str, List[float]] = defaultdict(list)

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


def evaluate_router_with_dr_ope(
    router: Router,
    source: DataSource,
    propensity_estimator: Optional[object] = None,
    reward_model: Optional[RewardModel] = None,
    use_dr_ope: bool = False,
) -> EvaluationReport:
    """Run ``router`` over ``source``; optionally compute DR-OPE alongside match-IPS.

    Args:
        router: Router policy to evaluate.
        source: DataSource yielding AnnotatedDecision records.
        propensity_estimator: Optional propensity estimator
            (must have estimate(task_type, difficulty, model) -> float method).
            If None and use_dr_ope=True, uses AnnotationConditionedEmpirical
            from warmup split (if available).
        reward_model: Optional reward model q̂(x, a) (must have
            predict(decision, model) -> float method).
            If None and use_dr_ope=True, uses DummyRewardModel.
        use_dr_ope: If True, compute both match-IPS and DR-OPE metrics.
            If False, compute match-IPS only (default, F3.1 behavior).

    Returns:
        EvaluationReport with match-IPS metrics always populated.
        If use_dr_ope=True, dr_quality and dr_cost are also populated.
    """
    # Always compute match-IPS
    match_ips_result = evaluate_router(router, source)

    # If DR-OPE not requested, return early
    if not use_dr_ope:
        return match_ips_result

    # DR-OPE requested: need propensity + reward estimators
    from .dr_ope import _compute_dr_ope
    from .propensity_estimator import AnnotationConditionedEmpirical
    from .reward_model import DummyRewardModel

    if propensity_estimator is None:
        raise ValueError(
            "DR-OPE requested but propensity_estimator not provided. "
            "Pass AnnotationConditionedEmpirical or compatible estimator."
        )

    if reward_model is None:
        # Default: use DummyRewardModel with mean quality estimate
        # For better results in Phase 3, pass RoutcastWrapper(routecast_instance)
        reward_model = DummyRewardModel(0.75)

    # Compute DR-OPE
    dr_ope_result = _compute_dr_ope(router, source, propensity_estimator, reward_model)

    # Merge results: return both match-IPS and DR-OPE
    return EvaluationReport(
        n_rows=match_ips_result.n_rows,
        n_matches=match_ips_result.n_matches,
        mean_quality=match_ips_result.mean_quality,
        mean_cost=match_ips_result.mean_cost,
        per_difficulty=match_ips_result.per_difficulty,
        # Add DR-OPE metrics
        dr_quality=dr_ope_result.dr_quality,
        dr_cost=dr_ope_result.dr_cost,
        per_difficulty_dr={
            diff: {
                "dr_quality": metrics.dr_quality,
                "dr_cost": metrics.dr_cost,
                "coverage": metrics.coverage,
            }
            for diff, metrics in dr_ope_result.per_difficulty.items()
        },
    )


__all__ = [
    "BucketMetrics",
    "EvaluationReport",
    "evaluate_router",
    "evaluate_router_with_dr_ope",
]
