"""Tests for DR-OPE (doubly-robust off-policy evaluation)."""

import pytest

from causal_agent_bench.dr_ope import DROPEMetrics, DROPEReport, _compute_dr_ope
from causal_agent_bench.loader import InMemoryDataSource
from causal_agent_bench.propensity_estimator import AnnotationConditionedEmpirical
from causal_agent_bench.reward_model import DummyRewardModel
from causal_agent_bench.router import RandomRouter
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def test_dropoe_metrics_coverage():
    """DROPEMetrics should compute coverage correctly."""
    metrics = DROPEMetrics(
        n_rows=100,
        n_matches=50,
        dr_quality=0.8,
        dr_cost=0.2,
    )
    assert metrics.coverage == 0.5


def test_dropoe_metrics_coverage_zero():
    """Coverage with zero rows should be 0.0."""
    metrics = DROPEMetrics(
        n_rows=0,
        n_matches=0,
        dr_quality=0.0,
        dr_cost=0.0,
    )
    assert metrics.coverage == 0.0


def test_dropoe_report_coverage():
    """DROPEReport should compute coverage from matches."""
    report = DROPEReport(
        n_rows=100,
        n_matches=75,
        dr_quality=0.8,
        dr_cost=0.15,
    )
    assert report.coverage == 0.75


def test_compute_dr_ope_identity():
    """With perfect propensity and reward model, DR-OPE should match observed."""
    # Create deterministic decisions where router always matches
    decisions = [
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id=f"d{i}",
                prompt=f"prompt_{i}",
                candidate_models=["gpt-3.5"],
                selected_model="gpt-3.5",
                observed_cost=0.1,
                observed_quality=0.8,
            ),
            annotation=CausalAnnotation(
                task_type="qa_factual",
                difficulty="easy",
                annotator_id="test",
                confidence=1.0,
            ),
        )
        for i in range(10)
    ]

    # Propensity estimator from same data (so it matches exactly)
    propensity_est = AnnotationConditionedEmpirical(decisions)

    # Dummy reward model that returns observed quality on match
    class ObservedRewardModel:
        def predict(self, decision, model):
            # Return observed quality for matched rows
            return decision.observed_quality

    reward_est = ObservedRewardModel()
    router = RandomRouter(seed=0)  # Will pick first candidate (gpt-3.5)
    source = InMemoryDataSource(decisions)

    report = _compute_dr_ope(router, source, propensity_est, reward_est)

    # All decisions match (only 1 candidate), so all rows count
    assert report.n_rows == 10
    # Since router matches log choice and reward is perfect
    assert abs(report.dr_quality - 0.8) < 0.01


def test_compute_dr_ope_empty():
    """Empty source should handle gracefully."""
    propensity_est = AnnotationConditionedEmpirical([])
    reward_est = DummyRewardModel(0.5)
    router = RandomRouter()
    source = InMemoryDataSource([])

    report = _compute_dr_ope(router, source, propensity_est, reward_est)
    assert report.n_rows == 0
    assert report.n_matches == 0
    assert report.dr_quality == 0.0


def test_compute_dr_ope_per_difficulty():
    """DR-OPE should stratify by difficulty."""
    decisions = [
        # Easy examples
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id="d_easy",
                prompt="Q",
                candidate_models=["gpt-3.5"],
                selected_model="gpt-3.5",
                observed_cost=0.05,
                observed_quality=0.9,
            ),
            annotation=CausalAnnotation(
                task_type="qa_factual",
                difficulty="easy",
                annotator_id="test",
                confidence=1.0,
            ),
        ),
        # Hard examples
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id="d_hard",
                prompt="Q",
                candidate_models=["claude"],
                selected_model="claude",
                observed_cost=0.3,
                observed_quality=0.7,
            ),
            annotation=CausalAnnotation(
                task_type="qa_factual",
                difficulty="hard",
                annotator_id="test",
                confidence=1.0,
            ),
        ),
    ]

    propensity_est = AnnotationConditionedEmpirical(decisions)

    class MatchingRewardModel:
        def predict(self, decision, model):
            return decision.observed_quality

    reward_est = MatchingRewardModel()
    router = RandomRouter(seed=0)
    source = InMemoryDataSource(decisions)

    report = _compute_dr_ope(router, source, propensity_est, reward_est)

    # Check overall
    assert report.n_rows == 2

    # Check per-difficulty
    assert "easy" in report.per_difficulty
    assert "hard" in report.per_difficulty
    assert abs(report.per_difficulty["easy"].dr_quality - 0.9) < 0.01
    assert abs(report.per_difficulty["hard"].dr_quality - 0.7) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
