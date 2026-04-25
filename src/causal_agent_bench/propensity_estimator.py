"""Propensity estimation for DR-OPE: log-policy model selection frequencies.

AnnotationConditionedEmpirical estimates π₀(model | task_type, difficulty)
from warmup data using annotation-stratified contingency tables with
Dirichlet smoothing.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .schema import AnnotatedDecision


class AnnotationConditionedEmpirical:
    """π₀(a | task_type, difficulty) from warmup decision history.

    Builds a contingency table over task_type × difficulty × selected_model
    from historical decisions, applies Dirichlet smoothing, and estimates
    the marginal propensity of each model given (task_type, difficulty).

    The resulting propensity estimates are used in DR-OPE to weight the
    importance-sampling correction term.
    """

    def __init__(
        self,
        warmup_decisions: List[AnnotatedDecision],
        alpha: float = 1.0,
    ) -> None:
        """Initialize propensity estimator from warmup data.

        Args:
            warmup_decisions: List of AnnotatedDecision records from warmup split.
            alpha: Dirichlet smoothing parameter (default 1.0 = uniform pseudocount).
        """
        self.alpha = alpha
        self.counts: Dict[Tuple[str, str, str], int] = defaultdict(int)
        self.totals: Dict[Tuple[str, str], int] = defaultdict(int)
        self.available_models: set = set()

        for ad in warmup_decisions:
            task_type = ad.annotation.task_type
            difficulty = ad.annotation.difficulty
            model = ad.decision.selected_model

            key = (task_type, difficulty)
            model_key = (task_type, difficulty, model)

            self.counts[model_key] += 1
            self.totals[key] += 1
            self.available_models.add(model)

        self.available_models = sorted(self.available_models)

    def estimate(
        self,
        task_type: str,
        difficulty: str,
        model: str,
    ) -> float:
        """Estimate π₀(model | task_type, difficulty).

        Returns smoothed frequency of model selection in (task_type, difficulty)
        stratum, or uniform fallback if stratum is empty.

        Args:
            task_type: Task type from CausalAnnotation.
            difficulty: Difficulty from CausalAnnotation.
            model: Model name to estimate propensity for.

        Returns:
            Propensity value in (0, 1].
        """
        key = (task_type, difficulty)
        total = self.totals.get(key, 0)
        model_count = self.counts.get((task_type, difficulty, model), 0)

        # Dirichlet smoother: (count + α) / (total + α × |models|)
        n_models = len(self.available_models) if self.available_models else 1
        denominator = total + self.alpha * n_models
        numerator = model_count + self.alpha

        return numerator / denominator if denominator > 0 else 1.0 / n_models


__all__ = ["AnnotationConditionedEmpirical"]
