"""ThompsonRouter (Beta-Bernoulli) tests."""

from __future__ import annotations

import pytest

from causal_agent_bench.loader import InMemoryDataSource
from causal_agent_bench.router import Router
from causal_agent_bench.routers.thompson import BetaArm, ThompsonRouter
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def _ad(idx: int, selected: str, quality: float, task: str = "qa_factual") -> AnnotatedDecision:
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
            difficulty="medium",
            annotator_id="test",
            confidence=0.9,
        ),
    )


class TestBetaArm:
    def test_default_prior_is_uniform(self):
        arm = BetaArm()
        assert arm.alpha == 1.0 and arm.beta == 1.0

    def test_update_splits_reward(self):
        arm = BetaArm()
        arm.update(0.75)
        assert arm.alpha == pytest.approx(1.75)
        assert arm.beta == pytest.approx(1.25)

    def test_update_clamps_out_of_range(self):
        arm = BetaArm()
        arm.update(1.5)  # treated as 1.0 → alpha += 1, beta += 0
        arm.update(-0.3)  # treated as 0.0 → alpha += 0, beta += 1
        assert arm.alpha == pytest.approx(2.0)
        assert arm.beta == pytest.approx(2.0)


class TestThompsonRouter:
    def test_satisfies_protocol(self):
        assert isinstance(ThompsonRouter(), Router)

    def test_seeded_deterministic(self):
        r1 = ThompsonRouter(seed=42)
        r2 = ThompsonRouter(seed=42)
        samples1 = [
            r1.route(decision=_ad(i, "a", 0.5).decision, annotation=_ad(i, "a", 0.5).annotation).selected_model
            for i in range(20)
        ]
        samples2 = [
            r2.route(decision=_ad(i, "a", 0.5).decision, annotation=_ad(i, "a", 0.5).annotation).selected_model
            for i in range(20)
        ]
        assert samples1 == samples2

    def test_fit_moves_posterior(self):
        r = ThompsonRouter(seed=0)
        before = r.posterior_mean("qa_factual", "a")
        # 50 observations of a=1.0 should push posterior mean near 1.0.
        source = InMemoryDataSource([_ad(i, "a", 1.0) for i in range(50)])
        r.fit(source)
        after = r.posterior_mean("qa_factual", "a")
        assert before == pytest.approx(0.5)
        assert after > 0.9

    def test_fit_isolates_by_task_type(self):
        r = ThompsonRouter(seed=0)
        source = InMemoryDataSource(
            [_ad(i, "a", 1.0, task="qa_factual") for i in range(10)]
            + [_ad(i + 100, "a", 0.0, task="code_generation") for i in range(10)]
        )
        r.fit(source)
        assert r.posterior_mean("qa_factual", "a") > 0.9
        assert r.posterior_mean("code_generation", "a") < 0.1

    def test_prefers_high_reward_arm_after_training(self):
        """After many observations, TS should lean heavily toward the better arm."""
        r = ThompsonRouter(seed=1)
        # "a" rewards high (~0.9), "b" low (~0.1), "c" mid (~0.5).
        source = InMemoryDataSource(
            [_ad(i, "a", 0.9) for i in range(40)]
            + [_ad(i + 100, "b", 0.1) for i in range(40)]
            + [_ad(i + 200, "c", 0.5) for i in range(40)]
        )
        r.fit(source)
        d = _ad(999, "a", 0.5)
        picks: dict = {}
        for _ in range(200):
            choice = r.route(decision=d.decision, annotation=d.annotation)
            picks[choice.selected_model] = picks.get(choice.selected_model, 0) + 1
        # "a" should dominate.
        assert picks.get("a", 0) > picks.get("b", 0)
        assert picks.get("a", 0) > picks.get("c", 0)
        assert picks.get("a", 0) >= 150  # majority

    def test_empty_candidates_raises(self):
        r = ThompsonRouter()
        bad_decision = RouterDecision(
            decision_id="x",
            prompt="p",
            candidate_models=[],
            selected_model="a",  # not in candidates, but required
            observed_cost=0.01,
            observed_quality=0.5,
        )
        ann = _ad(0, "a", 0.5).annotation
        with pytest.raises(ValueError, match="no candidate"):
            r.route(decision=bad_decision, annotation=ann)

    def test_posterior_mean_without_data_is_prior(self):
        r = ThompsonRouter()
        assert r.posterior_mean("qa_factual", "unseen-model") == 0.5
