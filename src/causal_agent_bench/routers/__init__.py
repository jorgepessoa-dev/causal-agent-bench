"""Additional Router implementations beyond the core baselines."""

from .popularity import PopularityRouter
from .thompson import ThompsonRouter

__all__ = ["PopularityRouter", "ThompsonRouter"]
