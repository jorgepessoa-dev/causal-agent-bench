"""Causal annotation schema for routing-decision records.

Extends upstream RouterBench outcomes with the metadata needed for
offline causal evaluation: task typing, difficulty estimates, and
declared latent confounders.

Design notes
------------
- Pydantic v2 for runtime validation and deterministic serialization.
- Enums are open-ended (`Literal[...]` + a fallback `str` variant) so
  new task types / difficulty buckets don't break old records.
- `confounders` is a free-form list of strings — we explicitly do NOT
  try to enumerate every possible latent factor. Convention:
  `"domain:finance"`, `"user_tier:free"`, `"time_of_day:peak"`, etc.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TaskType = Literal[
    "qa_factual",
    "qa_opinion",
    "code_generation",
    "code_explanation",
    "summarization",
    "translation",
    "classification",
    "math_reasoning",
    "logical_reasoning",
    "creative_writing",
    "chitchat",
    "other",
]

Difficulty = Literal["trivial", "easy", "medium", "hard", "adversarial"]


class CausalAnnotation(BaseModel):
    """Causal metadata attached to a router outcome.

    Annotators (human or LLM) produce these to enrich RouterBench rows.
    Each field is independently editable in a review UI.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    task_type: TaskType
    difficulty: Difficulty
    confounders: List[str] = Field(
        default_factory=list,
        description="Declared latent factors, format 'namespace:value'.",
    )
    annotator_id: str = Field(
        description="Annotator identifier (human login or LLM model/version)."
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Annotator's self-reported confidence."
    )
    notes: Optional[str] = Field(
        default=None, max_length=500, description="Optional free-text."
    )


class RouterDecision(BaseModel):
    """Single router decision record from an upstream dataset.

    Minimal shape — richer upstream fields stay in `extra` for
    round-tripping. Converters live in `causal_agent_bench.loader`.
    """

    model_config = ConfigDict(extra="allow", frozen=True)

    decision_id: str
    prompt: str
    candidate_models: List[str]
    selected_model: str
    observed_cost: float = Field(ge=0.0)
    observed_quality: float = Field(ge=0.0, le=1.0)
    propensity: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="If available from logging policy."
    )


class AnnotatedDecision(BaseModel):
    """RouterDecision + CausalAnnotation pair, ready for harness input."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision: RouterDecision
    annotation: CausalAnnotation


__all__ = [
    "AnnotatedDecision",
    "CausalAnnotation",
    "Difficulty",
    "RouterDecision",
    "TaskType",
]
