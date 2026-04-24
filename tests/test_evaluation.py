"""Evaluation harness tests."""

from __future__ import annotations

import pytest

from causal_agent_bench.evaluation import evaluate_router
from causal_agent_bench.loader import InMemoryDataSource
from causal_agent_bench.router import HeuristicRouter, Router, RouterChoice
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def _ad(
    idx: int,
    *,
    selected: str,
    quality: float,
    cost: float,
    difficulty: str = "medium",
    candidates=None,
) -> AnnotatedDecision:
    return AnnotatedDecision(
        decision=RouterDecision(
            decision_id=f"d{idx}",
            prompt=f"p{idx}",
            candidate_models=candidates or ["gpt-3.5", "gpt-4", "claude-3-opus"],
            selected_model=selected,
            observed_cost=cost,
            observed_quality=quality,
        ),
        annotation=CausalAnnotation(
            task_type="qa_factual",
            difficulty=difficulty,
            annotator_id="test",
            confidence=0.9,
        ),
    )


class _FixedRouter:
    """Always picks the same model, for deterministic coverage tests."""

    def __init__(self, model: str) -> None:
        self._model = model

    def route(self, *, decision, annotation) -> RouterChoice:
        return RouterChoice(selected_model=self._model, propensity=None)


class TestEvaluateRouter:
    def test_fixed_router_matches_only_subset(self):
        source = InMemoryDataSource(
            [
                _ad(1, selected="gpt-3.5", quality=0.5, cost=0.001),
                _ad(2, selected="gpt-4", quality=0.9, cost=0.01),
                _ad(3, selected="gpt-3.5", quality=0.6, cost=0.001),
            ]
        )
        router = _FixedRouter("gpt-3.5")
        assert isinstance(router, Router)
        report = evaluate_router(router, source)
        assert report.n_rows == 3
        assert report.n_matches == 2
        assert report.coverage == pytest.approx(2 / 3)
        assert report.mean_quality == pytest.approx(0.55)
        assert report.mean_cost == pytest.approx(0.001)

    def test_empty_source_returns_zero_metrics(self):
        report = evaluate_router(_FixedRouter("gpt-3.5"), InMemoryDataSource([]))
        assert report.n_rows == 0
        assert report.n_matches == 0
        assert report.coverage == 0.0
        assert report.mean_quality == 0.0
        assert report.mean_cost == 0.0

    def test_per_difficulty_bucketing(self):
        source = InMemoryDataSource(
            [
                _ad(1, selected="gpt-3.5", quality=0.5, cost=0.001, difficulty="easy"),
                _ad(2, selected="gpt-3.5", quality=0.4, cost=0.001, difficulty="easy"),
                _ad(3, selected="gpt-4", quality=0.9, cost=0.01, difficulty="hard"),
            ]
        )
        router = _FixedRouter("gpt-3.5")
        report = evaluate_router(router, source)
        assert set(report.per_difficulty.keys()) == {"easy", "hard"}
        easy = report.per_difficulty["easy"]
        assert easy.n_rows == 2
        assert easy.n_matches == 2
        assert easy.mean_quality == pytest.approx(0.45)
        hard = report.per_difficulty["hard"]
        assert hard.n_rows == 1
        assert hard.n_matches == 0
        assert hard.coverage == 0.0
        assert hard.mean_quality == 0.0

    def test_heuristic_router_end_to_end(self):
        source = InMemoryDataSource(
            [
                _ad(1, selected="gpt-3.5", quality=0.7, cost=0.001, difficulty="trivial"),
                _ad(2, selected="claude-3-opus", quality=0.95, cost=0.02, difficulty="hard"),
                _ad(3, selected="gpt-4", quality=0.88, cost=0.01, difficulty="medium"),
            ]
        )
        router = HeuristicRouter()
        report = evaluate_router(router, source)
        assert report.n_rows == 3
        assert report.n_matches == 3
        assert report.coverage == 1.0

    def test_rejects_non_annotated_decision(self):
        class _BadSource:
            def __iter__(self):
                yield "not-an-ad"

            def __len__(self):
                return 1

        with pytest.raises(TypeError, match="AnnotatedDecision"):
            evaluate_router(_FixedRouter("gpt-3.5"), _BadSource())
