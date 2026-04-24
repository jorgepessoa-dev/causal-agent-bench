"""Thompson-sampling router with Beta-Bernoulli posteriors per (task_type, model).

This is the first *learning* baseline in the benchmark. It maintains a Beta
posterior for each (task_type, model) pair over the observed_quality signal:

- ``alpha``: pseudo-successes (starts at 1.0)
- ``beta``: pseudo-failures (starts at 1.0)
- On observation ``q ∈ [0, 1]``: ``alpha += q``, ``beta += 1 - q``

At decision time we sample from each candidate's posterior and pick argmax.
Propensity is NOT tracked exactly (would require integrating over the max of
K Beta samples); we leave it ``None`` and rely on match-IPS evaluation.

The router is deliberately simple: no context beyond the annotated task_type,
no exploration bonus beyond Thompson's native posterior variance, no fallback
to a prior model when the posterior is uninformative (the Beta(1, 1) prior
does the work). Subclasses can override hooks to add structure.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

from ..router import RouterChoice
from ..schema import AnnotatedDecision, CausalAnnotation, RouterDecision, TaskType


@dataclass
class BetaArm:
    alpha: float = 1.0
    beta: float = 1.0

    def update(self, reward: float) -> None:
        reward = max(0.0, min(1.0, float(reward)))
        self.alpha += reward
        self.beta += 1.0 - reward

    def sample(self, rng: random.Random) -> float:
        return rng.betavariate(self.alpha, self.beta)


@dataclass
class ThompsonRouter:
    """Per-(task_type, model) Beta-Bernoulli Thompson sampler."""

    seed: int = 0
    _rng: random.Random = field(init=False)
    _arms: Dict[Tuple[TaskType, str], BetaArm] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def _arm(self, task_type: TaskType, model: str) -> BetaArm:
        key = (task_type, model)
        if key not in self._arms:
            self._arms[key] = BetaArm()
        return self._arms[key]

    def observe(
        self,
        *,
        task_type: TaskType,
        model: str,
        reward: float,
    ) -> None:
        """Single-observation posterior update."""
        self._arm(task_type, model).update(reward)

    def fit(self, source: Iterable[AnnotatedDecision]) -> "ThompsonRouter":
        """Batch-update posteriors from a DataSource-like iterable."""
        for ad in source:
            self.observe(
                task_type=ad.annotation.task_type,
                model=ad.decision.selected_model,
                reward=ad.decision.observed_quality,
            )
        return self

    def posterior_mean(self, task_type: TaskType, model: str) -> float:
        arm = self._arms.get((task_type, model))
        if arm is None:
            return 0.5  # Beta(1, 1) prior mean
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
            arm = self._arm(annotation.task_type, model)
            sample = arm.sample(self._rng)
            if sample > best_sample:
                best_sample = sample
                best_model = model
        assert best_model is not None  # candidates non-empty
        return RouterChoice(selected_model=best_model, propensity=None)


__all__ = ["BetaArm", "ThompsonRouter"]
