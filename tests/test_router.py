"""Router Protocol + baseline tests."""

from __future__ import annotations

import pytest

from causal_agent_bench.router import (
    HeuristicRouter,
    RandomRouter,
    Router,
)
from causal_agent_bench.schema import CausalAnnotation, RouterDecision


def _decision(candidates, selected="gpt-3.5") -> RouterDecision:
    return RouterDecision(
        decision_id="d",
        prompt="p",
        candidate_models=list(candidates),
        selected_model=selected,
        observed_cost=0.01,
        observed_quality=0.8,
    )


def _annotation(difficulty="medium") -> CausalAnnotation:
    return CausalAnnotation(
        task_type="qa_factual",
        difficulty=difficulty,
        annotator_id="test",
        confidence=0.9,
    )


class TestRandomRouter:
    def test_satisfies_protocol(self):
        assert isinstance(RandomRouter(), Router)

    def test_seeded_deterministic(self):
        r1 = RandomRouter(seed=42)
        r2 = RandomRouter(seed=42)
        d = _decision(["a", "b", "c", "d"])
        a = _annotation()
        choices1 = [r1.route(decision=d, annotation=a).selected_model for _ in range(10)]
        choices2 = [r2.route(decision=d, annotation=a).selected_model for _ in range(10)]
        assert choices1 == choices2

    def test_propensity_uniform(self):
        r = RandomRouter()
        d = _decision(["a", "b", "c", "d"])
        choice = r.route(decision=d, annotation=_annotation())
        assert choice.propensity == pytest.approx(0.25)

    def test_empty_candidates_raises(self):
        r = RandomRouter()
        with pytest.raises(ValueError, match="no candidate"):
            r.route(decision=_decision([]), annotation=_annotation())


class TestHeuristicRouter:
    def test_satisfies_protocol(self):
        assert isinstance(HeuristicRouter(), Router)

    def test_picks_cheap_for_trivial(self):
        r = HeuristicRouter()
        d = _decision(["gpt-3.5", "gpt-4"])
        c = r.route(decision=d, annotation=_annotation("trivial"))
        assert c.selected_model == "gpt-3.5"

    def test_picks_strong_for_hard(self):
        r = HeuristicRouter()
        d = _decision(["gpt-3.5", "gpt-4", "claude-3-opus"])
        c = r.route(decision=d, annotation=_annotation("hard"))
        assert c.selected_model == "claude-3-opus"

    def test_fallback_when_ladder_misses(self):
        r = HeuristicRouter()
        d = _decision(["custom-a", "custom-b"])
        c = r.route(decision=d, annotation=_annotation("hard"))
        # Ladder has no match → fall back to first candidate.
        assert c.selected_model == "custom-a"

    def test_custom_ladder_overrides(self):
        r = HeuristicRouter(
            ladders={"medium": ["custom-a"]},
        )
        d = _decision(["gpt-3.5", "custom-a"])
        c = r.route(decision=d, annotation=_annotation("medium"))
        assert c.selected_model == "custom-a"

    def test_empty_candidates_raises(self):
        r = HeuristicRouter()
        with pytest.raises(ValueError, match="no candidate"):
            r.route(decision=_decision([]), annotation=_annotation())
