"""Command-line evaluator: run a baseline router over a JSONL dataset.

Usage::

    python -m causal_agent_bench.cli \\
        --source tests/fixtures/synthetic_router_decisions.jsonl \\
        --router heuristic \\
        --output report.json

The goal is a one-liner that produces a deterministic JSON report suitable
for leaderboard ingestion (F2.4). Router choices: ``random``, ``heuristic``.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, TextIO

from .evaluation import EvaluationReport, evaluate_router
from .loaders import RouterBenchJsonlLoader
from .router import HeuristicRouter, RandomRouter, Router


_ROUTERS = ("random", "heuristic")


def _build_router(name: str, *, seed: int) -> Router:
    if name == "random":
        return RandomRouter(seed=seed)
    if name == "heuristic":
        return HeuristicRouter()
    raise ValueError(f"unknown router: {name}; choose from {_ROUTERS}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="causal-agent-bench",
        description="Evaluate a baseline router over a RouterBench-shaped JSONL file.",
    )
    p.add_argument("--source", required=True, type=Path, help="JSONL input file.")
    p.add_argument(
        "--router",
        required=True,
        choices=_ROUTERS,
        help="Baseline router to evaluate.",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Seed for stochastic routers (default: 0).",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON report to this path (default: stdout).",
    )
    return p


def _report_to_dict(
    router_name: str, source_path: Path, report: EvaluationReport
) -> Dict[str, Any]:
    per_difficulty = {
        diff: asdict(m) | {"coverage": m.coverage}
        for diff, m in report.per_difficulty.items()
    }
    return {
        "router": router_name,
        "source": str(source_path),
        "n_rows": report.n_rows,
        "n_matches": report.n_matches,
        "coverage": report.coverage,
        "mean_quality": report.mean_quality,
        "mean_cost": report.mean_cost,
        "per_difficulty": per_difficulty,
    }


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    stdout: Optional[TextIO] = None,
) -> int:
    args = _build_parser().parse_args(argv)
    out = stdout if stdout is not None else sys.stdout

    router = _build_router(args.router, seed=args.seed)
    source = RouterBenchJsonlLoader(args.source)
    report = evaluate_router(router, source)

    payload = _report_to_dict(args.router, args.source, report)
    encoded = json.dumps(payload, indent=2, sort_keys=True)

    if args.output is not None:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        out.write(encoded + "\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
