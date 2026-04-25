"""Tests for reward model wrappers."""

import pytest

from causal_agent_bench.reward_model import DummyRewardModel, RewardModel
from causal_agent_bench.schema import RouterDecision


def test_dummy_reward_model():
    """DummyRewardModel should return constant value."""
    model = DummyRewardModel(default_quality=0.75)
    decision = RouterDecision(
        decision_id="d1",
        prompt="test",
        candidate_models=["gpt-3.5", "claude"],
        selected_model="gpt-3.5",
        observed_cost=0.1,
        observed_quality=0.8,
    )
    # Should return default for any model
    assert model.predict(decision, "gpt-3.5") == 0.75
    assert model.predict(decision, "claude") == 0.75
    assert model.predict(decision, "unknown") == 0.75


def test_reward_model_protocol():
    """RewardModel protocol should accept any class with predict method."""
    model = DummyRewardModel(0.5)
    assert isinstance(model, RewardModel)


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
