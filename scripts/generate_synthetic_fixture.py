"""Generate a reproducible, larger synthetic fixture for local leaderboard runs.

Why this exists: the 3-row hand-crafted fixture exercises the harness's
shape but is too small to differentiate routers on ``mean_quality``
(ties are near-guaranteed). This script emits ``N`` rows with:

- seeded randomness (single CLI flag)
- plausible prompts bucketed by difficulty
- a realistic cost/quality structure where stronger models tend to score
  higher on hard prompts but cost more
- occasional router mismatches so ``coverage`` varies meaningfully

Output is RouterBench-shaped JSONL (same schema as
``tests/fixtures/synthetic_router_decisions.jsonl``), ready to be fed to
``causal_agent_bench.leaderboard_cli`` or any Router-aware consumer.

Run::

    python scripts/generate_synthetic_fixture.py \\
        --n 500 \\
        --seed 0 \\
        --output tests/fixtures/synthetic_router_decisions_large.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

MODELS: List[str] = [
    "gpt-3.5",
    "mistral-7b-instruct",
    "claude-3-haiku",
    "gpt-4",
    "claude-3-sonnet",
    "claude-3-opus",
]

# Per-model base cost (USD) + base quality ceiling. Hard prompts pull the
# quality down; easy prompts pull it up. Stronger models stay closer to
# ceiling on hard prompts.
_MODEL_PROFILE: Dict[str, Tuple[float, float]] = {
    "gpt-3.5": (0.0004, 0.72),
    "mistral-7b-instruct": (0.0002, 0.68),
    "claude-3-haiku": (0.0006, 0.76),
    "gpt-4": (0.0120, 0.91),
    "claude-3-sonnet": (0.0030, 0.86),
    "claude-3-opus": (0.0250, 0.94),
}

# Difficulty → rough quality-pull factor. Hard prompts lose more quality
# for weak models.
_DIFFICULTY_PULL: Dict[str, float] = {
    "trivial": 0.05,
    "easy": 0.10,
    "medium": 0.20,
    "hard": 0.40,
    "adversarial": 0.55,
}

_PROMPT_BANK: Dict[str, List[str]] = {
    "trivial": [
        "What is 2+2?",
        "Capital of France?",
        "Is the sky blue?",
        "Spell 'benchmark'.",
        "Define 'CPU'.",
    ],
    "easy": [
        "Write a haiku about recursion.",
        "Summarise this 200-word paragraph.",
        "Translate 'bonjour' to English.",
        "Is binary search O(log n)?",
        "Name three primary colors.",
    ],
    "medium": [
        "Explain BGP route flapping.",
        "What is the bias-variance tradeoff?",
        "Write a regex for matching IPv4 addresses.",
        "Compare REST and gRPC for internal services.",
        "Summarise the CAP theorem in one paragraph.",
    ],
    "hard": [
        "Prove Fermat's little theorem.",
        "Derive the Kalman filter update equations.",
        "Design a lock-free ring buffer and argue correctness.",
        "Explain Bareinboim's do-calculus with an example.",
        "Analyse the convergence guarantees of TD(lambda).",
    ],
    "adversarial": [
        "If P=NP, outline a reduction from 3-SAT to graph-isomorphism.",
        "Describe a zero-knowledge proof for Hamiltonian cycle.",
        "Reconcile the Banach-Tarski paradox with measure theory.",
        "Why does the category of sets fail to have a terminal coalgebra for P?",
        "Explain the Halting-problem undecidability proof in constructive logic.",
    ],
}

_TASK_TYPES: List[str] = [
    "qa_factual",
    "math_reasoning",
    "code_generation",
    "logical_reasoning",
    "summarization",
    "creative_writing",
]


def _sample_quality(model: str, difficulty: str, rng: random.Random) -> float:
    base = _MODEL_PROFILE[model][1]
    pull = _DIFFICULTY_PULL[difficulty]
    # Stronger models shrug off difficulty more; weaker ones collapse.
    strength = _MODEL_PROFILE[model][1]  # reuse ceiling as crude strength proxy
    resistance = 1.0 - (1.0 - strength) * 0.8
    quality = base - pull * (1.0 - resistance)
    # Noise floor / ceiling.
    quality += rng.gauss(0.0, 0.05)
    return float(max(0.0, min(1.0, quality)))


def _cost(model: str, rng: random.Random) -> float:
    base = _MODEL_PROFILE[model][0]
    return float(max(0.0, base * (1.0 + rng.gauss(0.0, 0.1))))


def _sample_candidates(rng: random.Random) -> List[str]:
    size = rng.randint(2, 4)
    return sorted(rng.sample(MODELS, size))


def _pick_logged_model(candidates: List[str], difficulty: str, rng: random.Random) -> str:
    """Simulate an upstream router: usually picks a strong model on hard prompts,
    cheap model on trivial prompts, with some noise."""
    if rng.random() < 0.15:
        return rng.choice(candidates)  # noise
    # rank candidates by ceiling; on hard pick top, on easy pick bottom.
    ranked = sorted(candidates, key=lambda m: _MODEL_PROFILE[m][1])
    if difficulty in ("trivial", "easy"):
        return ranked[0]
    if difficulty in ("hard", "adversarial"):
        return ranked[-1]
    return ranked[len(ranked) // 2]


def generate_row(idx: int, rng: random.Random) -> Dict[str, object]:
    difficulty = rng.choices(
        population=list(_DIFFICULTY_PULL.keys()),
        weights=[2, 3, 5, 3, 1],  # medium-heavy, some extremes
        k=1,
    )[0]
    prompt = rng.choice(_PROMPT_BANK[difficulty])
    task_type = rng.choice(_TASK_TYPES)
    candidates = _sample_candidates(rng)
    logged = _pick_logged_model(candidates, difficulty, rng)
    quality = _sample_quality(logged, difficulty, rng)
    row: Dict[str, object] = {
        "sample_id": f"synth-{idx:05d}",
        "prompt": prompt,
        "models": candidates,
        "model": logged,
        "cost": _cost(logged, rng),
        "score": quality,
        "difficulty": difficulty,
        "task_type": task_type,
    }
    return row


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, required=True, help="Row count.")
    ap.add_argument("--seed", type=int, default=0, help="RNG seed (default: 0).")
    ap.add_argument("--output", type=Path, required=True, help="Destination JSONL.")
    args = ap.parse_args(argv)

    rng = random.Random(args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        for i in range(args.n):
            fh.write(json.dumps(generate_row(i, rng)) + "\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
