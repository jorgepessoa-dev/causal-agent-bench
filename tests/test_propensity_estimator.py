"""Tests for AnnotationConditionedEmpirical propensity estimator."""

import pytest

from causal_agent_bench.propensity_estimator import AnnotationConditionedEmpirical
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def test_propensity_estimator_empty():
    """Empty warmup should handle gracefully."""
    est = AnnotationConditionedEmpirical([])
    # Uniform fallback when no data
    assert est.estimate("qa_factual", "easy", "gpt-3.5") == 1.0  # 1/1 models (empty set)


def test_propensity_estimator_uniform_single_model():
    """Single model in stratum should have propensity 1.0."""
    decisions = [
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id="d1",
                prompt="Q",
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
        ),
    ]
    est = AnnotationConditionedEmpirical(decisions)
    # With Dirichlet smoothing α=1: (count + 1) / (total + 1*|models|)
    # count=1, total=1, models=1
    # propensity = (1 + 1) / (1 + 1*1) = 2/2 = 1.0
    assert est.estimate("qa_factual", "easy", "gpt-3.5") == 1.0


def test_propensity_estimator_two_models():
    """Two equally-selected models should have propensity ~0.5 each."""
    decisions = [
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id=f"d{i}",
                prompt="Q",
                candidate_models=["gpt-3.5", "claude"],
                selected_model="gpt-3.5" if i % 2 == 0 else "claude",
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
    est = AnnotationConditionedEmpirical(decisions)
    # Each model selected 5 times, total=10, alpha=1, 2 models
    # propensity = (5 + 1) / (10 + 1*2) = 6/12 = 0.5
    assert abs(est.estimate("qa_factual", "easy", "gpt-3.5") - 0.5) < 0.01
    assert abs(est.estimate("qa_factual", "easy", "claude") - 0.5) < 0.01


def test_propensity_estimator_stratification():
    """Different strata should have independent propensities."""
    decisions = [
        # Easy: always gpt-3.5
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id="d_easy",
                prompt="Q",
                candidate_models=["gpt-3.5", "claude"],
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
        ),
        # Hard: always claude
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id="d_hard",
                prompt="Q",
                candidate_models=["gpt-3.5", "claude"],
                selected_model="claude",
                observed_cost=0.5,
                observed_quality=0.95,
            ),
            annotation=CausalAnnotation(
                task_type="qa_factual",
                difficulty="hard",
                annotator_id="test",
                confidence=1.0,
            ),
        ),
    ]
    est = AnnotationConditionedEmpirical(decisions)
    # Easy: gpt-3.5 always
    easy_gpt = est.estimate("qa_factual", "easy", "gpt-3.5")
    easy_claude = est.estimate("qa_factual", "easy", "claude")
    assert easy_gpt > easy_claude  # gpt-3.5 more likely in easy

    # Hard: claude always
    hard_gpt = est.estimate("qa_factual", "hard", "gpt-3.5")
    hard_claude = est.estimate("qa_factual", "hard", "claude")
    assert hard_claude > hard_gpt  # claude more likely in hard


def test_propensity_estimator_unseen_stratum():
    """Unseen (task, difficulty) strata should fall back to uniform."""
    decisions = [
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id="d1",
                prompt="Q",
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
        ),
    ]
    est = AnnotationConditionedEmpirical(decisions)
    # Unseen (qa_opinion, hard)
    prop = est.estimate("qa_opinion", "hard", "gpt-3.5")
    # Fallback: 1.0 / num_available_models = 1/1 (only gpt-3.5 seen)
    assert prop == 1.0


def test_propensity_estimator_dirichlet_smoothing():
    """Dirichlet smoothing should prevent zero propensities."""
    decisions = [
        AnnotatedDecision(
            decision=RouterDecision(
                decision_id="d1",
                prompt="Q",
                candidate_models=["gpt-3.5", "claude"],
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
        ),
    ]
    est = AnnotationConditionedEmpirical(decisions, alpha=1.0)
    # gpt-3.5 observed once, claude never
    # gpt-3.5: (1 + 1) / (1 + 1*2) = 2/3 ≈ 0.667
    # claude: (0 + 1) / (1 + 1*2) = 1/3 ≈ 0.333
    gpt_prop = est.estimate("qa_factual", "easy", "gpt-3.5")
    claude_prop = est.estimate("qa_factual", "easy", "claude")
    assert gpt_prop > 0  # Never zero due to smoothing
    assert claude_prop > 0  # Never zero due to smoothing
    assert abs(gpt_prop - 2 / 3) < 0.01
    assert abs(claude_prop - 1 / 3) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
