"""Combined-leaderboard runner.

Executes N routers against one dataset and returns a single ranked report.
This is what the F2.4 GitHub Actions workflow will call once we want a
single artifact per run (rather than one artifact per matrix row).

Ranking: currently by ``mean_quality`` desc, with ``coverage`` as tiebreaker.
Cost-weighted and Pareto rankings land when causal-agent-router's SCM is
wired in.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterator, List, Sequence, Tuple

from .evaluation import EvaluationReport, evaluate_router
from .loader import DataSource
from .router import Router
from .schema import AnnotatedDecision


@dataclass(frozen=True)
class LeaderboardEntry:
    router: str
    report: EvaluationReport


@dataclass(frozen=True)
class LeaderboardResult:
    entries: List[LeaderboardEntry]

    def ranked(self) -> List[LeaderboardEntry]:
        """By mean_quality desc; coverage as tiebreaker; router name as final tiebreaker."""
        return sorted(
            self.entries,
            key=lambda e: (
                -e.report.mean_quality,
                -e.report.coverage,
                e.router,
            ),
        )

    def to_dict(self) -> Dict[str, object]:
        ranked = self.ranked()
        return {
            "ranking": [e.router for e in ranked],
            "results": [
                {
                    "router": e.router,
                    "n_rows": e.report.n_rows,
                    "n_matches": e.report.n_matches,
                    "coverage": e.report.coverage,
                    "mean_quality": e.report.mean_quality,
                    "mean_cost": e.report.mean_cost,
                    "per_difficulty": {
                        diff: asdict(m) | {"coverage": m.coverage}
                        for diff, m in e.report.per_difficulty.items()
                    },
                }
                for e in ranked
            ],
        }


class _ReplayableSource:
    """Internal DataSource that re-iterates a materialized list."""

    def __init__(self, rows: List[AnnotatedDecision]) -> None:
        self._rows = rows

    def __iter__(self) -> Iterator[AnnotatedDecision]:
        return iter(self._rows)

    def __len__(self) -> int:
        return len(self._rows)


def run_leaderboard(
    routers: Sequence[Tuple[str, Router]],
    source: DataSource,
) -> LeaderboardResult:
    """Evaluate each ``(name, router)`` pair over ``source``.

    The source is materialized into a list before running — each router
    needs to walk it independently, and we cannot assume the DataSource is
    re-iterable.
    """
    materialized: List[AnnotatedDecision] = list(source)
    replayable = _ReplayableSource(materialized)

    entries: List[LeaderboardEntry] = []
    for name, router in routers:
        if not isinstance(router, Router):
            raise TypeError(f"router {name!r} does not satisfy Router protocol")
        report = evaluate_router(router, replayable)
        entries.append(LeaderboardEntry(router=name, report=report))
    return LeaderboardResult(entries=entries)


__all__ = ["LeaderboardEntry", "LeaderboardResult", "run_leaderboard"]
