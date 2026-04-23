"""Smoke test: package imports and version is sane."""

import causal_agent_bench


def test_package_imports():
    assert causal_agent_bench is not None


def test_version_defined():
    assert causal_agent_bench.__version__ == "0.0.1"
