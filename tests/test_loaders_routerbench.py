"""RouterBenchJsonlLoader + row mapping tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from causal_agent_bench.loaders import RouterBenchJsonlLoader, map_row_to_decision
from causal_agent_bench.loader import DataSource
from causal_agent_bench.schema import CausalAnnotation


FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_router_decisions.jsonl"


class TestMapRow:
    def test_correct_column_coerced_to_quality(self):
        d = map_row_to_decision(
            {
                "sample_id": "x1",
                "prompt": "p",
                "models": ["a", "b"],
                "model": "a",
                "cost": 0.01,
                "correct": 1,
            }
        )
        assert d.decision_id == "x1"
        assert d.observed_quality == 1.0
        assert d.candidate_models == ["a", "b"]

    def test_score_column_used_when_no_correct(self):
        d = map_row_to_decision(
            {
                "sample_id": "x2",
                "prompt": "p",
                "models": ["a"],
                "model": "a",
                "cost": 0.01,
                "score": 0.77,
            }
        )
        assert d.observed_quality == 0.77

    def test_missing_quality_field_raises(self):
        with pytest.raises(ValueError, match="quality"):
            map_row_to_decision(
                {
                    "sample_id": "x3",
                    "prompt": "p",
                    "models": ["a"],
                    "model": "a",
                    "cost": 0.01,
                }
            )

    def test_missing_id_raises(self):
        with pytest.raises(ValueError, match="decision_id"):
            map_row_to_decision(
                {
                    "prompt": "p",
                    "models": ["a"],
                    "model": "a",
                    "cost": 0.01,
                    "correct": 1,
                }
            )

    def test_extra_fields_preserved(self):
        d = map_row_to_decision(
            {
                "sample_id": "x4",
                "prompt": "p",
                "models": ["a"],
                "model": "a",
                "cost": 0.01,
                "correct": 1,
                "router": "learned-v1",
                "upstream_run_id": "rb-batch-7",
            }
        )
        assert d.model_extra == {"router": "learned-v1", "upstream_run_id": "rb-batch-7"}


class TestRouterBenchJsonlLoader:
    def test_satisfies_protocol(self):
        loader = RouterBenchJsonlLoader(FIXTURE)
        assert isinstance(loader, DataSource)

    def test_len_matches_line_count(self):
        loader = RouterBenchJsonlLoader(FIXTURE)
        assert len(loader) == 3

    def test_iteration_yields_annotated_decisions(self):
        loader = RouterBenchJsonlLoader(FIXTURE)
        rows = list(loader)
        assert len(rows) == 3
        assert rows[0].decision.decision_id == "rb-1"
        assert rows[1].decision.selected_model == "claude-3-opus"
        assert rows[2].decision.observed_quality == 0.0

    def test_default_annotation_is_placeholder(self):
        loader = RouterBenchJsonlLoader(FIXTURE)
        first = next(iter(loader))
        assert first.annotation.annotator_id == "unannotated"
        assert first.annotation.confidence == 0.0

    def test_custom_default_annotation(self):
        custom = CausalAnnotation(
            task_type="qa_factual",
            difficulty="easy",
            annotator_id="haiku-smoke",
            confidence=0.6,
        )
        loader = RouterBenchJsonlLoader(FIXTURE, default_annotation=custom)
        first = next(iter(loader))
        assert first.annotation == custom

    def test_len_is_cached(self):
        loader = RouterBenchJsonlLoader(FIXTURE)
        n1 = len(loader)
        # Second call returns the cached value — should match even if file
        # were mutated (we only guarantee consistency within a loader
        # instance). Asserted by equality after repeat call.
        assert len(loader) == n1

    def test_invalid_json_raises_with_location(self, tmp_path: Path):
        bad = tmp_path / "bad.jsonl"
        bad.write_text(
            '{"sample_id": "ok", "prompt": "p", "models": ["a"], "model": "a", "cost": 0.01, "correct": 1}\n'
            "not-json\n"
        )
        loader = RouterBenchJsonlLoader(bad)
        with pytest.raises(ValueError, match="Invalid JSON"):
            list(loader)

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            RouterBenchJsonlLoader(tmp_path / "does-not-exist.jsonl")

    def test_blank_lines_skipped(self, tmp_path: Path):
        p = tmp_path / "gappy.jsonl"
        p.write_text(
            '{"sample_id": "a", "prompt": "p", "models": ["a"], "model": "a", "cost": 0.01, "correct": 1}\n'
            "\n"
            '{"sample_id": "b", "prompt": "p", "models": ["a"], "model": "a", "cost": 0.01, "correct": 0}\n'
        )
        loader = RouterBenchJsonlLoader(p)
        assert len(loader) == 2
        assert [row.decision.decision_id for row in loader] == ["a", "b"]

    def test_inline_annotation_fields_override_default(self, tmp_path: Path):
        p = tmp_path / "annotated.jsonl"
        p.write_text(
            '{"sample_id": "a", "prompt": "p", "models": ["x"], "model": "x", '
            '"cost": 0.01, "correct": 1, "task_type": "code_generation", '
            '"difficulty": "hard", "annotator_id": "haiku-v1", "confidence": 0.85}\n'
            '{"sample_id": "b", "prompt": "p", "models": ["x"], "model": "x", '
            '"cost": 0.01, "correct": 0}\n'
        )
        loader = RouterBenchJsonlLoader(p)
        rows = list(loader)
        assert rows[0].annotation.task_type == "code_generation"
        assert rows[0].annotation.difficulty == "hard"
        assert rows[0].annotation.annotator_id == "haiku-v1"
        assert rows[0].annotation.confidence == 0.85
        # Row without annotation fields falls back to the placeholder default.
        assert rows[1].annotation.annotator_id == "unannotated"

    def test_inline_annotation_not_leaked_to_router_decision_extras(self, tmp_path: Path):
        p = tmp_path / "annotated.jsonl"
        p.write_text(
            '{"sample_id": "a", "prompt": "p", "models": ["x"], "model": "x", '
            '"cost": 0.01, "score": 0.5, "task_type": "math_reasoning", '
            '"difficulty": "medium", "router": "rb-v1"}\n'
        )
        loader = RouterBenchJsonlLoader(p)
        row = next(iter(loader))
        # annotation fields filtered out of RouterDecision.model_extra
        assert "task_type" not in (row.decision.model_extra or {})
        assert "difficulty" not in (row.decision.model_extra or {})
        # legitimate extras still pass through
        assert (row.decision.model_extra or {}).get("router") == "rb-v1"
