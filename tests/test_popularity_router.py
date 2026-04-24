"""PopularityRouter tests."""

from __future__ import annotations

import pytest

from causal_agent_bench.routers import PopularityRouter
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def _ad(idx: int, selected: str, task_type: str = "qa_factual") -> AnnotatedDecision:
    return AnnotatedDecision(
        decision=RouterDecision(
            decision_id=f"d{idx}",
            prompt=f"p{idx}",
            candidate_models=["a", "b", "c"],
            selected_model=selected,
            observed_cost=0.01,
            observed_quality=0.5,
        ),
        annotation=CausalAnnotation(
            task_type=task_type,
            difficulty="medium",
            annotator_id="t",
            confidence=0.9,
        ),
    )


class TestPopularityRouter:
    def test_picks_most_frequent_in_warmup(self):
        r = PopularityRouter()
        r.fit([_ad(i, "b") for i in range(5)] + [_ad(i + 10, "a") for i in range(3)])
        # "b" has 5 picks, "a" has 3, "c" has 0 → route should pick "b".
        out = r.route(decision=_ad(99, "a").decision, annotation=_ad(99, "a").annotation)
        assert out.selected_model == "b"
        assert out.propensity is None

    def test_separates_by_task_type(self):
        r = PopularityRouter()
        r.fit(
            [_ad(i, "a", task_type="qa_factual") for i in range(3)]
            + [_ad(i + 10, "c", task_type="code_generation") for i in range(4)]
        )
        qa = _ad(99, "a", task_type="qa_factual")
        code = _ad(99, "a", task_type="code_generation")
        assert r.route(decision=qa.decision, annotation=qa.annotation).selected_model == "a"
        assert r.route(decision=code.decision, annotation=code.annotation).selected_model == "c"

    def test_stable_tiebreak_by_candidate_order(self):
        # No warmup → all counts zero → picks first candidate.
        r = PopularityRouter()
        out = r.route(
            decision=_ad(1, "a").decision,
            annotation=_ad(1, "a").annotation,
        )
        assert out.selected_model == "a"

    def test_empty_candidates_raises(self):
        r = PopularityRouter()
        bad = RouterDecision(
            decision_id="x",
            prompt="p",
            candidate_models=[],
            selected_model="a",
            observed_cost=0.0,
            observed_quality=0.0,
        )
        with pytest.raises(ValueError):
            r.route(
                decision=bad,
                annotation=_ad(1, "a").annotation,
            )

    def test_count_method(self):
        r = PopularityRouter()
        r.fit([_ad(i, "b") for i in range(7)])
        assert r.count("qa_factual", "b") == 7
        assert r.count("qa_factual", "a") == 0
