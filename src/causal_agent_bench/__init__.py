"""causal-agent-bench: public benchmark for causal LLM routing.

Pre-alpha. Public API surfaces the pieces needed to run the F2.3 baseline
evaluation: schema types, the ``DataSource`` protocol + in-memory/JSONL
loaders, the ``Router`` protocol + baseline routers, and the evaluation
harness.
"""

from .evaluation import BucketMetrics, EvaluationReport, evaluate_router
from .loader import DataSource, InMemoryDataSource
from .loaders import RouterBenchJsonlLoader
from .router import HeuristicRouter, RandomRouter, Router, RouterChoice
from .schema import AnnotatedDecision, CausalAnnotation, Difficulty, RouterDecision, TaskType

__version__ = "0.0.2"

__all__ = [
    "AnnotatedDecision",
    "BucketMetrics",
    "CausalAnnotation",
    "DataSource",
    "Difficulty",
    "EvaluationReport",
    "HeuristicRouter",
    "InMemoryDataSource",
    "RandomRouter",
    "Router",
    "RouterBenchJsonlLoader",
    "RouterChoice",
    "RouterDecision",
    "TaskType",
    "evaluate_router",
    "__version__",
]
