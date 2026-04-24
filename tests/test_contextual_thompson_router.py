"""ContextualThompsonRouter tests — per (task_type, difficulty, model) posteriors."""

from __future__ import annotations

import pytest

from causal_agent_bench.loader import InMemoryDataSource
from causal_agent_bench.router import Router
from causal_agent_bench.routers.contextual_thompson import ContextualThompsonRouter
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def _ad(
    idx: int,
    selected: str,
    quality: float,
    *,
    task: str = "qa_factual",
    difficulty: str = "medium",
) -> AnnotatedDecision:
    return AnnotatedDecision(
        decision=RouterDecision(
            decision_id=f"d{idx}",
            prompt=f"p{idx}",
            candidate_models=["a", "b", "c"],
            selected_model=selected,
            observed_cost=0.01,
            observed_quality=quality,
        ),
        annotation=CausalAnnotation(
            task_type=task,
            difficulty=difficulty,
            annotator_id="test",
            confidence=0.9,
        ),
    )


class TestContextualThompsonRouter:
    def test_satisfies_protocol(self):
        assert isinstance(ContextualThompsonRouter(), Router)

    def test_seeded_deterministic(self):
        r1 = ContextualThompsonRouter(seed=42)
        r2 = ContextualThompsonRouter(seed=42)
        picks1 = [
            r1.route(decision=_ad(i, "a", 0.5).decision, annotation=_ad(i, "a", 0.5).annotation).selected_model
            for i in range(20)
        ]
        picks2 = [
            r2.route(decision=_ad(i, "a", 0.5).decision, annotation=_ad(i, "a", 0.5).annotation).selected_model
            for i in range(20)
        ]
        assert picks1 == picks2

    def test_fit_stratifies_by_difficulty(self):
        """Same (task_type, model) but different difficulty → independent posteriors."""
        r = ContextualThompsonRouter(seed=0)
        source = InMemoryDataSource(
            [_ad(i, "a", 1.0, difficulty="easy") for i in range(20)]
            + [_ad(i + 100, "a", 0.0, difficulty="hard") for i in range(20)]
        )
        r.fit(source)
        assert r.posterior_mean("qa_factual", "easy", "a") > 0.9
        assert r.posterior_mean("qa_factual", "hard", "a") < 0.1

    def test_posterior_mean_without_data_is_prior(self):
        r = ContextualThompsonRouter()
        assert r.posterior_mean("qa_factual", "medium", "unseen") == 0.5

    def test_empty_candidates_raises(self):
        r = ContextualThompsonRouter()
        bad = RouterDecision(
            decision_id="x",
            prompt="p",
            candidate_models=[],
            selected_model="a",
            observed_cost=0.01,
            observed_quality=0.5,
        )
        ann = _ad(0, "a", 0.5).annotation
        with pytest.raises(ValueError, match="no candidate"):
            r.route(decision=bad, annotation=ann)

    def test_flat_vs_contextual_disagree_when_difficulty_confounds(self):
        """If a model is strong on easy and weak on hard, the flat Thompson pools;
        contextual keeps them separate. Check: on a *hard* decision after mixed
        training, contextual should rarely pick the model that was strong only
        on easy prompts."""
        from causal_agent_bench.routers.thompson import ThompsonRouter

        training = InMemoryDataSource(
            [_ad(i, "a", 1.0, difficulty="easy") for i in range(40)]
            + [_ad(i + 100, "a", 0.0, difficulty="hard") for i in range(40)]
            + [_ad(i + 200, "b", 0.5, difficulty="easy") for i in range(40)]
            + [_ad(i + 300, "b", 0.5, difficulty="hard") for i in range(40)]
        )
        flat = ThompsonRouter(seed=2).fit(training)
        ctx = ContextualThompsonRouter(seed=2).fit(training)

        hard_query = _ad(999, "a", 0.5, difficulty="hard")
        flat_picks_a = sum(
            1
            for _ in range(200)
            if flat.route(decision=hard_query.decision, annotation=hard_query.annotation).selected_model == "a"
        )
        ctx_picks_a = sum(
            1
            for _ in range(200)
            if ctx.route(decision=hard_query.decision, annotation=hard_query.annotation).selected_model == "a"
        )
        assert ctx_picks_a < flat_picks_a
