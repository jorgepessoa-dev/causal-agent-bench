"""Schema validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def _make_decision(**overrides) -> RouterDecision:
    defaults = dict(
        decision_id="d1",
        prompt="What is 2+2?",
        candidate_models=["gpt-3.5", "gpt-4"],
        selected_model="gpt-3.5",
        observed_cost=0.001,
        observed_quality=0.9,
    )
    defaults.update(overrides)
    return RouterDecision(**defaults)


def _make_annotation(**overrides) -> CausalAnnotation:
    defaults = dict(
        task_type="qa_factual",
        difficulty="trivial",
        confounders=["domain:math"],
        annotator_id="claude-haiku-4.5",
        confidence=0.95,
    )
    defaults.update(overrides)
    return CausalAnnotation(**defaults)


class TestCausalAnnotation:
    def test_minimal_construction(self):
        a = _make_annotation()
        assert a.task_type == "qa_factual"
        assert a.confounders == ["domain:math"]

    def test_extra_forbidden(self):
        with pytest.raises(ValidationError):
            CausalAnnotation(
                task_type="qa_factual",
                difficulty="easy",
                annotator_id="x",
                confidence=0.5,
                unknown_field=1,
            )

    def test_invalid_task_type(self):
        with pytest.raises(ValidationError):
            _make_annotation(task_type="banana")

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            _make_annotation(confidence=1.5)
        with pytest.raises(ValidationError):
            _make_annotation(confidence=-0.1)

    def test_frozen(self):
        a = _make_annotation()
        with pytest.raises(ValidationError):
            a.confidence = 0.1  # type: ignore[misc]

    def test_notes_length_limit(self):
        with pytest.raises(ValidationError):
            _make_annotation(notes="x" * 501)


class TestRouterDecision:
    def test_extra_allowed(self):
        d = _make_decision(upstream_run_id="rb-42")
        assert d.model_extra == {"upstream_run_id": "rb-42"}

    def test_cost_nonneg(self):
        with pytest.raises(ValidationError):
            _make_decision(observed_cost=-0.01)

    def test_quality_bounds(self):
        with pytest.raises(ValidationError):
            _make_decision(observed_quality=1.5)

    def test_propensity_optional(self):
        d = _make_decision()
        assert d.propensity is None
        d2 = _make_decision(propensity=0.33)
        assert d2.propensity == 0.33


class TestAnnotatedDecision:
    def test_round_trip(self):
        ad = AnnotatedDecision(
            decision=_make_decision(),
            annotation=_make_annotation(),
        )
        dumped = ad.model_dump()
        restored = AnnotatedDecision(**dumped)
        assert restored == ad
