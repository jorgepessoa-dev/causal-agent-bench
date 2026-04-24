"""Smoke test: package imports and version is sane."""

import causal_agent_bench


def test_package_imports():
    assert causal_agent_bench is not None


def test_version_defined():
    assert causal_agent_bench.__version__ == "0.0.6"


def test_public_api_surface():
    expected = {
        "AnnotatedDecision",
        "BucketMetrics",
        "CausalAnnotation",
        "ContextualThompsonRouter",
        "DataSource",
        "Difficulty",
        "EvaluationReport",
        "HeuristicRouter",
        "InMemoryDataSource",
        "LeaderboardEntry",
        "LeaderboardResult",
        "PopularityRouter",
        "RandomRouter",
        "Router",
        "RouterBenchJsonlLoader",
        "RouterChoice",
        "RouterDecision",
        "TaskType",
        "ThompsonRouter",
        "evaluate_router",
        "run_leaderboard",
        "__version__",
    }
    assert expected <= set(causal_agent_bench.__all__)
    for name in expected:
        assert hasattr(causal_agent_bench, name), f"missing: {name}"
