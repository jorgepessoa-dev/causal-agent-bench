"""Combined-leaderboard runner tests."""

from __future__ import annotations

import pytest

from causal_agent_bench.leaderboard import (
    LeaderboardResult,
    run_leaderboard,
)
from causal_agent_bench.loader import InMemoryDataSource
from causal_agent_bench.router import RouterChoice
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


class _FixedRouter:
    def __init__(self, model: str) -> None:
        self._model = model

    def route(self, *, decision, annotation) -> RouterChoice:
        return RouterChoice(selected_model=self._model, propensity=None)


def _ad(idx: int, selected: str, quality: float) -> AnnotatedDecision:
    return AnnotatedDecision(
        decision=RouterDecision(
            decision_id=f"d{idx}",
            prompt=f"p{idx}",
            candidate_models=["a", "b"],
            selected_model=selected,
            observed_cost=0.01,
            observed_quality=quality,
        ),
        annotation=CausalAnnotation(
            task_type="qa_factual",
            difficulty="medium",
            annotator_id="t",
            confidence=0.9,
        ),
    )


class TestRunLeaderboard:
    def test_two_routers_ranked_by_quality(self):
        source = InMemoryDataSource(
            [
                _ad(1, "a", 0.9),
                _ad(2, "a", 0.8),
                _ad(3, "b", 0.1),
            ]
        )
        result = run_leaderboard(
            [("pick_a", _FixedRouter("a")), ("pick_b", _FixedRouter("b"))],
            source,
        )
        assert isinstance(result, LeaderboardResult)
        ranked = [e.router for e in result.ranked()]
        assert ranked == ["pick_a", "pick_b"]
        # Winner's quality should be the mean of {0.9, 0.8} = 0.85.
        top = result.ranked()[0]
        assert top.report.mean_quality == pytest.approx(0.85)

    def test_coverage_tiebreaks_when_quality_ties(self):
        # Both routers achieve 0.5 mean quality; differ in coverage.
        source = InMemoryDataSource(
            [
                _ad(1, "a", 0.5),
                _ad(2, "a", 0.5),
                _ad(3, "b", 0.5),
            ]
        )
        result = run_leaderboard(
            [("pick_a", _FixedRouter("a")), ("pick_b", _FixedRouter("b"))],
            source,
        )
        ranked = [e.router for e in result.ranked()]
        assert ranked == ["pick_a", "pick_b"]  # pick_a covers 2/3, pick_b 1/3

    def test_source_traversed_once_per_router_without_reiteration_bug(self):
        """Each router must see every row of the source."""
        source = InMemoryDataSource([_ad(i, "a", 0.5) for i in range(5)])
        result = run_leaderboard(
            [("r1", _FixedRouter("a")), ("r2", _FixedRouter("a"))],
            source,
        )
        for entry in result.entries:
            assert entry.report.n_rows == 5

    def test_to_dict_has_ranking_and_results(self):
        source = InMemoryDataSource([_ad(1, "a", 0.9), _ad(2, "b", 0.1)])
        result = run_leaderboard(
            [("pick_a", _FixedRouter("a")), ("pick_b", _FixedRouter("b"))],
            source,
        )
        d = result.to_dict()
        assert "ranking" in d
        assert "results" in d
        assert d["ranking"] == [e.router for e in result.ranked()]
        assert len(d["results"]) == 2
        assert {r["router"] for r in d["results"]} == {"pick_a", "pick_b"}

    def test_rejects_non_router(self):
        source = InMemoryDataSource([_ad(1, "a", 0.5)])
        with pytest.raises(TypeError, match="Router protocol"):
            run_leaderboard([("bad", object())], source)

    def test_empty_router_list(self):
        source = InMemoryDataSource([_ad(1, "a", 0.5)])
        result = run_leaderboard([], source)
        assert result.entries == []
        assert result.ranked() == []
