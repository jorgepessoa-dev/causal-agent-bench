"""Additional Router implementations beyond the core baselines."""

from .contextual_thompson import ContextualThompsonRouter
from .popularity import PopularityRouter
from .thompson import ThompsonRouter

__all__ = ["ContextualThompsonRouter", "PopularityRouter", "ThompsonRouter"]
