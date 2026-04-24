"""All-baselines leaderboard CLI.

Runs every registered baseline over a JSONL source and writes a single
ranked JSON report. Intended for the F2.4 GitHub Actions workflow:
one invocation, one artifact, deterministic ordering.

Usage::

    python -m causal_agent_bench.leaderboard_cli \\
        --source tests/fixtures/synthetic_router_decisions.jsonl \\
        --output leaderboard.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence, TextIO, Tuple

from .leaderboard import run_leaderboard
from .loader import InMemoryDataSource
from .loaders import RouterBenchJsonlLoader
from .router import HeuristicRouter, RandomRouter, Router
from .routers import PopularityRouter, ThompsonRouter


def _all_baselines(seed: int, warmup_source: Optional[Path]) -> List[Tuple[str, Router]]:
    baselines: List[Tuple[str, Router]] = [
        ("random", RandomRouter(seed=seed)),
        ("heuristic", HeuristicRouter()),
    ]
    popularity = PopularityRouter()
    thompson = ThompsonRouter(seed=seed)
    if warmup_source is not None:
        warm = list(RouterBenchJsonlLoader(warmup_source))
        popularity.fit(warm)
        thompson.fit(warm)
    baselines.append(("popularity", popularity))
    baselines.append(("thompson", thompson))
    return baselines


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="causal-agent-bench-leaderboard",
        description="Run all baseline routers and emit a combined ranked report.",
    )
    p.add_argument("--source", required=True, type=Path, help="JSONL input file.")
    p.add_argument(
        "--warmup",
        type=Path,
        default=None,
        help="Optional JSONL used to pre-fit learning routers (e.g. thompson).",
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


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    stdout: Optional[TextIO] = None,
) -> int:
    args = _build_parser().parse_args(argv)
    out = stdout if stdout is not None else sys.stdout

    raw_source = RouterBenchJsonlLoader(args.source)
    source = InMemoryDataSource(list(raw_source))  # materialize once

    routers = _all_baselines(seed=args.seed, warmup_source=args.warmup)
    result = run_leaderboard(routers, source)
    payload = {
        "source": str(args.source),
        "seed": args.seed,
        **result.to_dict(),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)

    if args.output is not None:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        out.write(encoded + "\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
