"""RouterBench JSONL loader.

Reads routing decisions from a JSONL file matching the RouterBench v1 schema
(see docs/upstream_sources.md). Emits `AnnotatedDecision` with a default
placeholder annotation; the annotator pipeline (Haiku-backed) fills real
`CausalAnnotation` values downstream.

Design choice: JSONL as the canonical on-disk format. RouterBench itself ships
parquet; we convert once at download time so downstream tools only need
stdlib. Parquet support can be layered on as a second loader without
disturbing this one.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from ..loader import ensure_path
from ..schema import AnnotatedDecision, CausalAnnotation, RouterDecision


_PLACEHOLDER_ANNOTATOR_ID = "unannotated"


def map_row_to_decision(row: Dict[str, Any]) -> RouterDecision:
    """Map a RouterBench-shaped dict to our RouterDecision.

    Accepts either `correct` (0/1) or `score` (float) for quality. Missing
    optional fields (propensity, router) are preserved as-is via Pydantic
    ``extra="allow"``.
    """
    quality = row.get("observed_quality")
    if quality is None:
        if "score" in row:
            quality = float(row["score"])
        elif "correct" in row:
            quality = float(row["correct"])
        else:
            raise ValueError(
                f"Row {row.get('sample_id', '?')} missing quality/score/correct field"
            )

    decision_id = row.get("decision_id") or row.get("sample_id")
    if decision_id is None:
        raise ValueError("Row missing decision_id/sample_id")

    candidates = row.get("candidate_models") or row.get("models")
    if not candidates:
        raise ValueError(f"Row {decision_id} missing candidate_models/models")

    selected = row.get("selected_model") or row.get("model")
    if selected is None:
        raise ValueError(f"Row {decision_id} missing selected_model/model")

    cost = row.get("observed_cost", row.get("cost"))
    if cost is None:
        raise ValueError(f"Row {decision_id} missing observed_cost/cost")

    extras = {
        k: v
        for k, v in row.items()
        if k
        not in {
            "decision_id",
            "sample_id",
            "prompt",
            "candidate_models",
            "models",
            "selected_model",
            "model",
            "observed_cost",
            "cost",
            "observed_quality",
            "score",
            "correct",
        }
    }

    return RouterDecision(
        decision_id=str(decision_id),
        prompt=row["prompt"],
        candidate_models=list(candidates),
        selected_model=str(selected),
        observed_cost=float(cost),
        observed_quality=float(quality),
        **extras,
    )


def _default_annotation() -> CausalAnnotation:
    return CausalAnnotation(
        task_type="other",
        difficulty="medium",
        annotator_id=_PLACEHOLDER_ANNOTATOR_ID,
        confidence=0.0,
    )


class RouterBenchJsonlLoader:
    """Lazy JSONL DataSource for RouterBench-shaped data.

    Does not load the full file into memory — each iteration streams the
    file. ``len()`` performs a one-time line-count scan (cached thereafter).
    """

    def __init__(
        self,
        path: str | Path,
        *,
        default_annotation: Optional[CausalAnnotation] = None,
    ) -> None:
        self._path = ensure_path(path)
        self._default_annotation = default_annotation or _default_annotation()
        self._cached_len: Optional[int] = None

    @property
    def path(self) -> Path:
        return self._path

    def __iter__(self) -> Iterator[AnnotatedDecision]:
        with self._path.open("r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at {self._path}:{lineno}: {exc.msg}"
                    ) from exc
                yield AnnotatedDecision(
                    decision=map_row_to_decision(row),
                    annotation=self._default_annotation,
                )

    def __len__(self) -> int:
        if self._cached_len is None:
            with self._path.open("r", encoding="utf-8") as fh:
                self._cached_len = sum(1 for line in fh if line.strip())
        return self._cached_len
