"""causal-agent-bench: public benchmark for causal LLM routing.

Pre-alpha. Public API surfaces the pieces needed to run the F2.3 baseline
evaluation: schema types, the ``DataSource`` protocol + in-memory/JSONL
loaders, the ``Router`` protocol + baseline routers, and the evaluation
harness.
"""

from .evaluation import BucketMetrics, EvaluationReport, evaluate_router
from .leaderboard import LeaderboardEntry, LeaderboardResult, run_leaderboard
from .loader import DataSource, InMemoryDataSource
from .loaders import RouterBenchJsonlLoader
from .router import HeuristicRouter, RandomRouter, Router, RouterChoice
from .routers import ThompsonRouter
from .schema import AnnotatedDecision, CausalAnnotation, Difficulty, RouterDecision, TaskType

__version__ = "0.0.4"

__all__ = [
    "AnnotatedDecision",
    "BucketMetrics",
    "CausalAnnotation",
    "DataSource",
    "Difficulty",
    "EvaluationReport",
    "HeuristicRouter",
    "InMemoryDataSource",
    "LeaderboardEntry",
    "LeaderboardResult",
    "RandomRouter",
    "Router",
    "RouterBenchJsonlLoader",
    "RouterChoice",
    "RouterDecision",
    "TaskType",
    "ThompsonRouter",
    "evaluate_router",
    "run_leaderboard",
    "__version__",
]
