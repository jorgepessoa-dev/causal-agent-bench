"""Data-source abstraction for annotated routing decisions.

F2.2 will provide a `RouterBenchLoader` as the first concrete implementation.
This module defines the Protocol only, plus an in-memory loader useful in
tests and for ad-hoc experimentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, List, Protocol, runtime_checkable

from .schema import AnnotatedDecision


@runtime_checkable
class DataSource(Protocol):
    """Iterable source of annotated routing decisions.

    Implementations should be lazy where possible (yield rows, don't load
    everything up front) — benchmark datasets can be 400k+ rows.
    """

    def __iter__(self) -> Iterator[AnnotatedDecision]: ...

    def __len__(self) -> int: ...


class InMemoryDataSource:
    """Simplest possible DataSource — wraps a list. For tests and small seeds."""

    def __init__(self, decisions: List[AnnotatedDecision]) -> None:
        self._decisions = list(decisions)

    def __iter__(self) -> Iterator[AnnotatedDecision]:
        return iter(self._decisions)

    def __len__(self) -> int:
        return len(self._decisions)


def count_rows(source: DataSource) -> int:
    """Utility: count rows by iteration (useful when `__len__` is expensive)."""
    return sum(1 for _ in source)


def ensure_path(p: str | Path) -> Path:
    """Normalize a path input; raise if it does not exist."""
    path = Path(p).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"DataSource path not found: {path}")
    return path


__all__ = ["DataSource", "InMemoryDataSource", "count_rows", "ensure_path"]
