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
from typing import Iterable, List, Optional, Sequence, TextIO, Tuple

from .leaderboard import run_leaderboard
from .loader import InMemoryDataSource
from .loaders import RouterBenchJsonlLoader
from .router import HeuristicRouter, RandomRouter, Router
from .routers import ContextualThompsonRouter, PopularityRouter, ThompsonRouter
from .schema import AnnotatedDecision


def _all_baselines(
    seed: int, fit_data: Optional[Iterable[AnnotatedDecision]]
) -> List[Tuple[str, Router]]:
    baselines: List[Tuple[str, Router]] = [
        ("random", RandomRouter(seed=seed)),
        ("heuristic", HeuristicRouter()),
    ]
    popularity = PopularityRouter()
    thompson = ThompsonRouter(seed=seed)
    contextual = ContextualThompsonRouter(seed=seed)
    if fit_data is not None:
        warm = list(fit_data)
        popularity.fit(warm)
        thompson.fit(warm)
        contextual.fit(warm)
    baselines.append(("popularity", popularity))
    baselines.append(("thompson", thompson))
    baselines.append(("contextual_thompson", contextual))
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
        help="Optional JSONL used to pre-fit learning routers. Mutually "
        "exclusive with --warmup-split.",
    )
    p.add_argument(
        "--warmup-split",
        type=int,
        default=0,
        help="Use the first N rows of --source as warmup, remaining as eval. "
        "0 disables (default). Mutually exclusive with --warmup.",
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

    if args.warmup is not None and args.warmup_split:
        raise SystemExit("--warmup and --warmup-split are mutually exclusive")

    all_rows = list(RouterBenchJsonlLoader(args.source))

    fit_data: Optional[List[AnnotatedDecision]]
    eval_rows: List[AnnotatedDecision]

    if args.warmup_split:
        if args.warmup_split <= 0 or args.warmup_split >= len(all_rows):
            raise SystemExit(
                f"--warmup-split={args.warmup_split} must be in (0, {len(all_rows)})"
            )
        fit_data = all_rows[: args.warmup_split]
        eval_rows = all_rows[args.warmup_split :]
    elif args.warmup is not None:
        fit_data = list(RouterBenchJsonlLoader(args.warmup))
        eval_rows = all_rows
    else:
        fit_data = None
        eval_rows = all_rows

    source = InMemoryDataSource(eval_rows)
    routers = _all_baselines(seed=args.seed, fit_data=fit_data)
    result = run_leaderboard(routers, source)
    payload = {
        "source": str(args.source),
        "seed": args.seed,
        "warmup_split": args.warmup_split or None,
        "warmup": str(args.warmup) if args.warmup else None,
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
