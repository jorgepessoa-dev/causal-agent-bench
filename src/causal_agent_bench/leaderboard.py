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

from .evaluation import EvaluationReport, evaluate_router, evaluate_router_with_dr_ope
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
        results = []
        for e in ranked:
            result_dict = {
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
            # Add DR-OPE metrics if present
            if e.report.dr_quality is not None:
                result_dict["dr_quality"] = e.report.dr_quality
            if e.report.dr_cost is not None:
                result_dict["dr_cost"] = e.report.dr_cost
            if e.report.per_difficulty_dr is not None:
                result_dict["per_difficulty_dr"] = e.report.per_difficulty_dr
            results.append(result_dict)
        return {
            "ranking": [e.router for e in ranked],
            "results": results,
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
    use_dr_ope: bool = False,
    warmup_data: List[AnnotatedDecision] | None = None,
) -> LeaderboardResult:
    """Evaluate each ``(name, router)`` pair over ``source``.

    The source is materialized into a list before running — each router
    needs to walk it independently, and we cannot assume the DataSource is
    re-iterable.

    Args:
        routers: List of (name, router) pairs to evaluate.
        source: DataSource yielding AnnotatedDecision records.
        use_dr_ope: If True, compute DR-OPE metrics alongside match-IPS.
            Requires warmup_data for propensity estimation.
        warmup_data: Optional list of AnnotatedDecision records for propensity
            estimation. Used only if use_dr_ope=True.
    """
    materialized: List[AnnotatedDecision] = list(source)
    replayable = _ReplayableSource(materialized)

    # Set up DR-OPE if requested
    propensity_estimator = None
    if use_dr_ope:
        if warmup_data is None or len(warmup_data) == 0:
            raise ValueError(
                "DR-OPE requested but warmup_data is empty or None. "
                "Set --warmup or --warmup-split > 0."
            )
        from .propensity_estimator import AnnotationConditionedEmpirical

        propensity_estimator = AnnotationConditionedEmpirical(
            warmup_decisions=warmup_data
        )

    entries: List[LeaderboardEntry] = []
    for name, router in routers:
        if not isinstance(router, Router):
            raise TypeError(f"router {name!r} does not satisfy Router protocol")

        if use_dr_ope:
            report = evaluate_router_with_dr_ope(
                router,
                replayable,
                propensity_estimator=propensity_estimator,
                reward_model=None,  # Will use default
                use_dr_ope=True,
            )
        else:
            report = evaluate_router(router, replayable)

        entries.append(LeaderboardEntry(router=name, report=report))
    return LeaderboardResult(entries=entries)


__all__ = ["LeaderboardEntry", "LeaderboardResult", "run_leaderboard"]
