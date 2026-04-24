"""Contextual Thompson-sampling router with Beta-Bernoulli posteriors
per (task_type, difficulty, model).

Adds one more confounder (difficulty) to the posterior key relative to the
global ``ThompsonRouter``. The intuition is causal: if difficulty is a
confounder (affects both the logged router's pick and the observed quality),
pooling over difficulty produces biased posteriors. Stratifying restores
within-stratum exchangeability — the minimal adjustment set for this DAG.

Trade-off: more granular buckets mean slower warmup (fewer samples per arm).
On small N this can *underperform* the flat version until enough data
accumulates per stratum. This is exactly the data-efficiency vs. bias trade
we want to measure on the benchmark.

No change to the update rule or propensity handling — we inherit the same
Beta(1, 1) prior and leave propensity ``None`` (match-IPS evaluation).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

from ..router import RouterChoice
from ..schema import AnnotatedDecision, CausalAnnotation, Difficulty, RouterDecision, TaskType
from .thompson import BetaArm


@dataclass
class ContextualThompsonRouter:
    """Per-(task_type, difficulty, model) Beta-Bernoulli Thompson sampler."""

    seed: int = 0
    _rng: random.Random = field(init=False)
    _arms: Dict[Tuple[TaskType, Difficulty, str], BetaArm] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def _arm(self, task_type: TaskType, difficulty: Difficulty, model: str) -> BetaArm:
        key = (task_type, difficulty, model)
        if key not in self._arms:
            self._arms[key] = BetaArm()
        return self._arms[key]

    def observe(
        self,
        *,
        task_type: TaskType,
        difficulty: Difficulty,
        model: str,
        reward: float,
    ) -> None:
        self._arm(task_type, difficulty, model).update(reward)

    def fit(self, source: Iterable[AnnotatedDecision]) -> "ContextualThompsonRouter":
        for ad in source:
            self.observe(
                task_type=ad.annotation.task_type,
                difficulty=ad.annotation.difficulty,
                model=ad.decision.selected_model,
                reward=ad.decision.observed_quality,
            )
        return self

    def posterior_mean(
        self, task_type: TaskType, difficulty: Difficulty, model: str
    ) -> float:
        arm = self._arms.get((task_type, difficulty, model))
        if arm is None:
            return 0.5
        return arm.alpha / (arm.alpha + arm.beta)

    def route(
        self,
        *,
        decision: RouterDecision,
        annotation: CausalAnnotation,
    ) -> RouterChoice:
        candidates = decision.candidate_models
        if not candidates:
            raise ValueError(f"{decision.decision_id}: no candidate models")
        best_model: Optional[str] = None
        best_sample = float("-inf")
        for model in candidates:
            arm = self._arm(annotation.task_type, annotation.difficulty, model)
            sample = arm.sample(self._rng)
            if sample > best_sample:
                best_sample = sample
                best_model = model
        assert best_model is not None
        return RouterChoice(selected_model=best_model, propensity=None)


__all__ = ["ContextualThompsonRouter"]
