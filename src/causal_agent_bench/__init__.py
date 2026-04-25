"""causal-agent-bench: public benchmark for causal LLM routing.

Pre-alpha. Public API surfaces the pieces needed to run the F2.3 baseline
evaluation: schema types, the ``DataSource`` protocol + in-memory/JSONL
loaders, the ``Router`` protocol + baseline routers, and the evaluation
harness. Adds DR-OPE support (Phase 1 validation, F3.2+).
"""

from .dr_ope import DROPEMetrics, DROPEReport
from .evaluation import BucketMetrics, EvaluationReport, evaluate_router, evaluate_router_with_dr_ope
from .leaderboard import LeaderboardEntry, LeaderboardResult, run_leaderboard
from .loader import DataSource, InMemoryDataSource
from .loaders import RouterBenchJsonlLoader
from .propensity_estimator import AnnotationConditionedEmpirical
from .reward_model import DummyRewardModel, RewardModel, RoutcastWrapper
from .router import HeuristicRouter, RandomRouter, Router, RouterChoice
from .routers import ContextualThompsonRouter, PopularityRouter, ThompsonRouter
from .schema import AnnotatedDecision, CausalAnnotation, Difficulty, RouterDecision, TaskType

__version__ = "0.0.6"

__all__ = [
    "AnnotatedDecision",
    "AnnotationConditionedEmpirical",
    "BucketMetrics",
    "CausalAnnotation",
    "ContextualThompsonRouter",
    "DROPEMetrics",
    "DROPEReport",
    "DataSource",
    "Difficulty",
    "DummyRewardModel",
    "EvaluationReport",
    "HeuristicRouter",
    "InMemoryDataSource",
    "LeaderboardEntry",
    "LeaderboardResult",
    "PopularityRouter",
    "RandomRouter",
    "RewardModel",
    "Router",
    "RouterBenchJsonlLoader",
    "RouterChoice",
    "RouterDecision",
    "RoutcastWrapper",
    "TaskType",
    "ThompsonRouter",
    "evaluate_router",
    "evaluate_router_with_dr_ope",
    "run_leaderboard",
    "__version__",
]
