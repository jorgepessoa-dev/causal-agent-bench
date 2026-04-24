"""Router Protocol + baseline implementations (F2.3).

A router, given a prompt + its annotation + a set of candidate models, picks
one model. We don't care how the router chose at evaluation time (only the
choice matters for scoring), but routers MAY expose a propensity for OPE.

Two baselines live here:

- ``RandomRouter``: uniform over candidates. Seeded for reproducibility.
- ``HeuristicRouter``: picks by difficulty/task_type. Cheap model for trivial/
  easy, strong model for hard/adversarial, configurable preference ladders.

Smarter baselines (RouteLLM reimpl, learned router, causal-agent-router) will
land in future commits as separate modules, all conforming to ``Router``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Protocol, Sequence, runtime_checkable

from .schema import CausalAnnotation, Difficulty, RouterDecision


@dataclass(frozen=True)
class RouterChoice:
    """Router's output for a single input."""

    selected_model: str
    propensity: Optional[float] = None


@runtime_checkable
class Router(Protocol):
    """A routing policy over a fixed candidate set per input.

    Routers MUST be deterministic given the same inputs and internal state.
    Stochastic routers (``RandomRouter``) achieve this via a seeded RNG.
    """

    def route(
        self,
        *,
        decision: RouterDecision,
        annotation: CausalAnnotation,
    ) -> RouterChoice: ...


class RandomRouter:
    """Uniform-random choice over ``decision.candidate_models``.

    Propensity is reported as ``1 / |candidates|`` (exactly uniform).
    """

    def __init__(self, *, seed: int = 0) -> None:
        self._rng = random.Random(seed)

    def route(
        self,
        *,
        decision: RouterDecision,
        annotation: CausalAnnotation,
    ) -> RouterChoice:
        candidates = decision.candidate_models
        if not candidates:
            raise ValueError(f"{decision.decision_id}: no candidate models")
        selected = self._rng.choice(candidates)
        return RouterChoice(
            selected_model=selected,
            propensity=1.0 / len(candidates),
        )


_DEFAULT_LADDER: Dict[Difficulty, Sequence[str]] = {
    "trivial": ("gpt-3.5", "mistral-7b", "haiku"),
    "easy": ("gpt-3.5", "mistral-7b", "haiku"),
    "medium": ("gpt-4", "claude-3-sonnet", "sonnet"),
    "hard": ("claude-3-opus", "gpt-4", "opus"),
    "adversarial": ("claude-3-opus", "gpt-4", "opus"),
}


class HeuristicRouter:
    """Picks by difficulty, using a configurable preference ladder.

    For each input, walk the ladder for that difficulty level and pick the
    first model that is present in ``decision.candidate_models``. If none
    match, fall back to the first candidate.
    """

    def __init__(
        self,
        *,
        ladders: Optional[Mapping[Difficulty, Sequence[str]]] = None,
    ) -> None:
        self._ladders: Dict[Difficulty, Sequence[str]] = dict(
            ladders if ladders is not None else _DEFAULT_LADDER
        )

    def route(
        self,
        *,
        decision: RouterDecision,
        annotation: CausalAnnotation,
    ) -> RouterChoice:
        candidates: List[str] = list(decision.candidate_models)
        if not candidates:
            raise ValueError(f"{decision.decision_id}: no candidate models")
        ladder = self._ladders.get(annotation.difficulty, ())
        for preferred in ladder:
            if preferred in candidates:
                return RouterChoice(selected_model=preferred, propensity=None)
        return RouterChoice(selected_model=candidates[0], propensity=None)


__all__ = [
    "HeuristicRouter",
    "RandomRouter",
    "Router",
    "RouterChoice",
]
