"""Popularity-baseline router: pick the historically most-selected candidate.

This is a deterministic "mode" baseline. It counts how often each model was
selected (conditioned on task type) in a warmup source and, at decision time,
picks the candidate with the highest count. Ties are broken by candidate
order in the decision (stable, deterministic).

Why this exists:
- It gives the leaderboard a defensible lower bound for any learning router.
  If Thompson (or any causal baseline) cannot beat "always pick what humans
  picked before", exploration/causal-correction is not paying off.
- It requires only observation counts, no reward signal — so it is robust to
  noisy or missing quality columns.

Caveats:
- No exploration. Rare models stay rare forever.
- Propensity is ``None`` (non-uniform, concentrated choice).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

from ..router import RouterChoice
from ..schema import AnnotatedDecision, CausalAnnotation, RouterDecision, TaskType


@dataclass
class PopularityRouter:
    """Pick the most-frequently-selected candidate in the warmup, per task type."""

    _counts: Dict[Tuple[TaskType, str], int] = field(
        default_factory=lambda: Counter(), init=False, repr=False
    )

    def observe(self, *, task_type: TaskType, model: str) -> None:
        self._counts[(task_type, model)] = self._counts.get((task_type, model), 0) + 1

    def fit(self, source: Iterable[AnnotatedDecision]) -> "PopularityRouter":
        for ad in source:
            self.observe(
                task_type=ad.annotation.task_type,
                model=ad.decision.selected_model,
            )
        return self

    def count(self, task_type: TaskType, model: str) -> int:
        return self._counts.get((task_type, model), 0)

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
        best_count = -1
        for model in candidates:  # stable left-to-right tiebreak
            c = self.count(annotation.task_type, model)
            if c > best_count:
                best_count = c
                best_model = model
        assert best_model is not None
        return RouterChoice(selected_model=best_model, propensity=None)


__all__ = ["PopularityRouter"]
