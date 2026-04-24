"""CLI smoke tests."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from causal_agent_bench.cli import main


FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_router_decisions.jsonl"


def _run(argv):
    buf = io.StringIO()
    rc = main(argv, stdout=buf)
    assert rc == 0
    return buf.getvalue()


class TestCLI:
    def test_heuristic_on_fixture_stdout(self):
        out = _run(["--source", str(FIXTURE), "--router", "heuristic"])
        payload = json.loads(out)
        assert payload["router"] == "heuristic"
        assert payload["n_rows"] == 3
        assert 0.0 <= payload["coverage"] <= 1.0

    def test_random_is_seed_stable(self):
        out1 = _run(["--source", str(FIXTURE), "--router", "random", "--seed", "7"])
        out2 = _run(["--source", str(FIXTURE), "--router", "random", "--seed", "7"])
        assert out1 == out2

    def test_output_file(self, tmp_path: Path):
        dest = tmp_path / "report.json"
        _run(
            [
                "--source", str(FIXTURE),
                "--router", "heuristic",
                "--output", str(dest),
            ]
        )
        payload = json.loads(dest.read_text())
        assert payload["router"] == "heuristic"
        assert "per_difficulty" in payload

    def test_rejects_unknown_router(self):
        with pytest.raises(SystemExit):
            main(["--source", str(FIXTURE), "--router", "bogus"])

    def test_rejects_missing_source(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            main(["--source", str(tmp_path / "nope.jsonl"), "--router", "random"])

    def test_per_difficulty_has_coverage_field(self):
        out = _run(["--source", str(FIXTURE), "--router", "heuristic"])
        payload = json.loads(out)
        for bucket in payload["per_difficulty"].values():
            assert "coverage" in bucket
            assert "mean_quality" in bucket
            assert "n_rows" in bucket
