"""DataSource protocol + in-memory loader tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from causal_agent_bench.loader import (
    DataSource,
    InMemoryDataSource,
    count_rows,
    ensure_path,
)
from causal_agent_bench.schema import (
    AnnotatedDecision,
    CausalAnnotation,
    RouterDecision,
)


def _sample_ad(i: int) -> AnnotatedDecision:
    return AnnotatedDecision(
        decision=RouterDecision(
            decision_id=f"d{i}",
            prompt=f"prompt-{i}",
            candidate_models=["m1", "m2"],
            selected_model="m1",
            observed_cost=0.01 * i,
            observed_quality=0.5,
        ),
        annotation=CausalAnnotation(
            task_type="qa_factual",
            difficulty="easy",
            annotator_id="test",
            confidence=0.8,
        ),
    )


class TestInMemoryDataSource:
    def test_iter_and_len(self):
        ds = InMemoryDataSource([_sample_ad(i) for i in range(5)])
        assert len(ds) == 5
        assert sum(1 for _ in ds) == 5

    def test_empty(self):
        ds = InMemoryDataSource([])
        assert len(ds) == 0
        assert list(ds) == []

    def test_satisfies_protocol(self):
        ds = InMemoryDataSource([])
        assert isinstance(ds, DataSource)

    def test_count_rows_matches_len(self):
        ds = InMemoryDataSource([_sample_ad(i) for i in range(3)])
        assert count_rows(ds) == len(ds)


class TestEnsurePath:
    def test_existing_path(self, tmp_path: Path):
        f = tmp_path / "exists.txt"
        f.write_text("x")
        assert ensure_path(f) == f.resolve()

    def test_missing_path(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            ensure_path(tmp_path / "nope.txt")
