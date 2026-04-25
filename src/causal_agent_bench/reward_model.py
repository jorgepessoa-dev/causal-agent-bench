"""Reward model wrappers for DR-OPE: quality estimation q̂(x, a).

Provides interfaces for plugging in reward estimators (Routecast, reference SCM,
or user-provided predictor) into the DR-OPE formula.
"""

from __future__ import annotations

from typing import Protocol, Optional, runtime_checkable

from .schema import RouterDecision


@runtime_checkable
class RewardModel(Protocol):
    """Protocol for reward model (quality estimator) q̂(x, a).

    Any class with a `predict(decision, model)` method conforming to
    this signature can be plugged into DR-OPE evaluation.
    """

    def predict(self, decision: RouterDecision, model: str) -> float:
        """Predict quality q̂(x, a) for a given decision and model.

        Args:
            decision: RouterDecision record (contains prompt, candidate_models, etc).
            model: Model name to predict quality for.

        Returns:
            Predicted quality in [0, 1] (or higher if unconstrained).
        """
        ...


class RoutcastWrapper:
    """Wrapper around Routecast (external package) for quality prediction.

    Routecast is a reference implementation of causal quality estimation
    using an SCM. It exposes predict_quality(prompt, model, annotation)
    which returns the posterior mean quality for (prompt, model).

    This wrapper adapts that interface to the RewardModel protocol.
    """

    def __init__(self, routecast_instance: Optional[object] = None) -> None:
        """Initialize Routecast wrapper.

        Args:
            routecast_instance: Optional pre-instantiated Routecast object.
                If None, will attempt lazy import and instantiation.
                Expected to have method:
                    predict_quality(prompt: str, model: str, annotation: CausalAnnotation) -> float
        """
        if routecast_instance is not None:
            self.routecast = routecast_instance
        else:
            self._routecast = self._lazy_load_routecast()

    def _lazy_load_routecast(self) -> object:
        """Lazy-load Routecast from pip install."""
        try:
            import routecast

            # Instantiate with default config
            # Adjust as needed for actual Routecast API
            return routecast.Routecast()
        except ImportError:
            raise ImportError(
                "routecast not installed. "
                "Install with: pip install routecast (from PyPI)"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Routecast: {e}")

    @property
    def routecast(self) -> object:
        """Lazy-loaded Routecast instance."""
        if not hasattr(self, "_routecast"):
            self._routecast = self._lazy_load_routecast()
        return self._routecast

    @routecast.setter
    def routecast(self, value: object) -> None:
        """Set Routecast instance (for testing or manual override)."""
        self._routecast = value

    def predict(self, decision: RouterDecision, model: str) -> float:
        """Predict quality using Routecast.predict_quality.

        Args:
            decision: RouterDecision (provides prompt, annotation via extra fields).
            model: Model name to predict quality for.

        Returns:
            Predicted quality (posterior mean from Routecast).
        """
        # Extract annotation from decision if available in extra fields
        annotation = decision.__dict__.get("annotation", None)

        return self.routecast.predict_quality(
            prompt=decision.prompt,
            model=model,
            annotation=annotation,
        )


class DummyRewardModel:
    """Dummy reward model for testing (returns fixed value or observed quality)."""

    def __init__(self, default_quality: float = 0.5) -> None:
        self.default_quality = default_quality

    def predict(self, decision: RouterDecision, model: str) -> float:
        """Return dummy quality (for testing only)."""
        # In testing, we might return observed_quality for matched decisions
        # or a fixed default for unmatched decisions
        return self.default_quality


class OracleRewardModel:
    """Oracle reward model: returns observed_quality from decision (for DR-OPE validation).

    This is an upper-bound estimator for Phase 3 synthetic validation.
    In real data, use RoutcastWrapper or a proper trained model.
    """

    def predict(self, decision: RouterDecision, model: str) -> float:
        """Return observed quality from decision record."""
        return decision.observed_quality


__all__ = ["RewardModel", "RoutcastWrapper", "DummyRewardModel", "OracleRewardModel"]
