"""Leaderboard CLI tests."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from causal_agent_bench.leaderboard_cli import main


FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_router_decisions.jsonl"


def _run(argv):
    buf = io.StringIO()
    rc = main(argv, stdout=buf)
    assert rc == 0
    return buf.getvalue()


class TestLeaderboardCLI:
    def test_runs_all_baselines(self):
        out = _run(["--source", str(FIXTURE)])
        payload = json.loads(out)
        assert "ranking" in payload
        assert set(payload["ranking"]) == {"random", "heuristic", "thompson"}
        assert payload["seed"] == 0
        assert payload["source"] == str(FIXTURE)

    def test_deterministic_across_runs(self):
        out1 = _run(["--source", str(FIXTURE), "--seed", "123"])
        out2 = _run(["--source", str(FIXTURE), "--seed", "123"])
        assert out1 == out2

    def test_output_file(self, tmp_path: Path):
        dest = tmp_path / "lb.json"
        _run(["--source", str(FIXTURE), "--output", str(dest)])
        payload = json.loads(dest.read_text())
        assert "results" in payload
        assert len(payload["results"]) == 3

    def test_warmup_affects_thompson(self, tmp_path: Path):
        # Build a warmup file where model "gpt-4" always wins.
        warm = tmp_path / "warm.jsonl"
        warm.write_text(
            "".join(
                f'{{"sample_id": "w{i}", "prompt": "p", "models": ["gpt-3.5", "gpt-4"], '
                f'"model": "gpt-4", "cost": 0.01, "correct": 1}}\n'
                for i in range(20)
            )
        )
        out_cold = _run(["--source", str(FIXTURE), "--seed", "0"])
        out_warm = _run(
            ["--source", str(FIXTURE), "--seed", "0", "--warmup", str(warm)]
        )
        # Warmup with gpt-4=always-good should not make the outputs IDENTICAL
        # (thompson posteriors differ) — assert at least one field differs
        # somewhere in the JSON.
        assert out_cold != out_warm

    def test_missing_source_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            main(["--source", str(tmp_path / "nope.jsonl")])

    def test_ranking_matches_results_order(self):
        out = _run(["--source", str(FIXTURE)])
        payload = json.loads(out)
        result_order = [r["router"] for r in payload["results"]]
        assert result_order == payload["ranking"]
