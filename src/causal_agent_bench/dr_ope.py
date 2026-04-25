"""Doubly-robust off-policy evaluation (DR-OPE) for router evaluation.

Implements the doubly-robust (DR) OPE formula from Dudik et al. (2011),
which combines direct method (reward model) with importance-sampling (propensity)
correction for bias reduction and variance control.

Formula:
  V_DR(π) = (1/n) Σᵢ [
      q̂(xᵢ, π(xᵢ)) +
      𝟙[π(xᵢ) = aᵢ] / π̂₀(aᵢ | xᵢ) × (qᵢ - q̂(xᵢ, aᵢ))
  ]

where:
  - q̂(x, a): reward model prediction
  - π₀: log-policy (baseline) propensity
  - π: evaluation policy (router)
  - q: observed outcome
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .loader import DataSource
from .propensity_estimator import AnnotationConditionedEmpirical
from .reward_model import RewardModel
from .router import Router
from .schema import AnnotatedDecision


@dataclass(frozen=True)
class DROPEMetrics:
    """DR-OPE evaluation result per bucket."""

    n_rows: int
    n_matches: int
    dr_quality: float  # DR-OPE estimated quality
    dr_cost: float  # DR-OPE estimated cost
    reward_mse: float = 0.0  # Reward model MSE on matched rows (for diagnostics)

    @property
    def coverage(self) -> float:
        """Fraction of rows where π(x) = π₀(x) (match)."""
        return self.n_matches / self.n_rows if self.n_rows else 0.0


@dataclass(frozen=True)
class DROPEReport:
    """Full DR-OPE evaluation report."""

    n_rows: int
    n_matches: int
    dr_quality: float  # Overall DR-OPE quality
    dr_cost: float  # Overall DR-OPE cost
    per_difficulty: Dict[str, DROPEMetrics] = field(default_factory=dict)

    @property
    def coverage(self) -> float:
        return self.n_matches / self.n_rows if self.n_rows else 0.0


def _compute_dr_ope(
    router: Router,
    source: DataSource,
    propensity_est: AnnotationConditionedEmpirical,
    reward_model: RewardModel,
) -> DROPEReport:
    """Compute DR-OPE metrics for a router over a data source.

    Args:
        router: Router policy to evaluate.
        source: DataSource yielding AnnotatedDecision records.
        propensity_est: Propensity estimator π̂₀(a | task_type, difficulty).
        reward_model: Reward model q̂(x, a).

    Returns:
        DROPEReport with overall and per-difficulty metrics.
    """
    total_rows = 0
    dr_qualities: List[float] = []
    dr_costs: List[float] = []
    reward_errors: List[float] = []

    bucket_totals: Dict[str, int] = {}
    bucket_dr_q: Dict[str, List[float]] = {}
    bucket_dr_c: Dict[str, List[float]] = {}
    bucket_errors: Dict[str, List[float]] = {}

    for ad in source:
        if not isinstance(ad, AnnotatedDecision):
            raise TypeError(f"Expected AnnotatedDecision, got {type(ad).__name__}")

        total_rows += 1
        diff = ad.annotation.difficulty
        task_type = ad.annotation.task_type

        # Ensure bucket exists
        if diff not in bucket_totals:
            bucket_totals[diff] = 0
            bucket_dr_q[diff] = []
            bucket_dr_c[diff] = []
            bucket_errors[diff] = []

        bucket_totals[diff] += 1

        # Evaluate policy choice
        choice = router.route(decision=ad.decision, annotation=ad.annotation)
        a_eval = choice.selected_model
        a_log = ad.decision.selected_model
        q_log = ad.decision.observed_quality
        c_log = ad.decision.observed_cost

        # Direct method term: q̂(x, π(x))
        q_pred_eval = reward_model.predict(ad.decision, a_eval)

        # IPS correction term (only if match)
        ips_q_term = 0.0
        ips_c_term = 0.0

        if a_eval == a_log:
            # Matched decision: can compute IPS correction
            propensity = propensity_est.estimate(task_type, diff, a_log)

            if propensity > 0:
                q_pred_log = reward_model.predict(ad.decision, a_log)
                c_pred_eval = reward_model.predict(ad.decision, a_eval)

                # IPS correction: (q - q̂) / π̂₀
                ips_q_term = (q_log - q_pred_log) / propensity
                # For cost, assume same structure
                ips_c_term = (c_log - c_pred_eval) / propensity

                # Record reward model error for diagnostics
                reward_errors.append(abs(q_log - q_pred_log))
                bucket_errors[diff].append(abs(q_log - q_pred_log))

        # DR estimate: direct + IPS correction
        dr_q = q_pred_eval + ips_q_term
        dr_c = q_pred_eval + ips_c_term  # Cost direct method + IPS

        dr_qualities.append(dr_q)
        dr_costs.append(dr_c)
        bucket_dr_q[diff].append(dr_q)
        bucket_dr_c[diff].append(dr_c)

    # Aggregate overall metrics
    mean_dr_q = sum(dr_qualities) / len(dr_qualities) if dr_qualities else 0.0
    mean_dr_c = sum(dr_costs) / len(dr_costs) if dr_costs else 0.0
    mean_reward_mse = (
        sum(e ** 2 for e in reward_errors) / len(reward_errors)
        if reward_errors
        else 0.0
    )

    # Per-difficulty metrics
    per_difficulty = {}
    for diff in bucket_totals:
        qs = bucket_dr_q[diff]
        cs = bucket_dr_c[diff]
        es = bucket_errors[diff]

        mean_q = sum(qs) / len(qs) if qs else 0.0
        mean_c = sum(cs) / len(cs) if cs else 0.0
        mse = sum(e ** 2 for e in es) / len(es) if es else 0.0

        per_difficulty[diff] = DROPEMetrics(
            n_rows=bucket_totals[diff],
            n_matches=len(qs),  # Rows where match occurred
            dr_quality=mean_q,
            dr_cost=mean_c,
            reward_mse=mse,
        )

    return DROPEReport(
        n_rows=total_rows,
        n_matches=len([q for q in dr_qualities if q is not None]),
        dr_quality=mean_dr_q,
        dr_cost=mean_dr_c,
        per_difficulty=per_difficulty,
    )


__all__ = ["DROPEMetrics", "DROPEReport", "_compute_dr_ope"]
