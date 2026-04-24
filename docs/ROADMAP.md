# Roadmap

## Phases (maps to CognitiveOS 2026 plan, F2)

| Phase | Scope | Status |
|-------|-------|--------|
| F2.1  | Scaffold — dir tree, LICENSE, README, CONTRIBUTING, pyproject, CI | ✅ shipped |
| F2.2  | Dataset seed — fork/extend RouterBench with causal annotations (task_type, difficulty, confounders) | 🟡 prep done (loader + schema + license checklist); real ingestion pending dedicated session |
| F2.3  | Baselines — random, heuristic, popularity, thompson, causal (Routecast) | 🟡 4 of 5 shipped; Routecast blocked on F3.2 PyPI publish |
| F2.4  | Leaderboard — single combined ranked artifact per commit via GitHub Actions | ✅ shipped |
| F2.5  | Docs — README deepening, contribution template, submission guide, metric definitions | ⏳ |

## Dependencies

- **RouterBench** (withmartian/routerbench) — upstream dataset (Apache-2.0 check required at F2.2).
- **lm-evaluation-harness** (EleutherAI) — inspirational structure for harness (not imported directly).
- **Routecast** — reference causal router (separate repo; first baseline).
- **CognitiveOS** (github.com/jorgepessoa-dev/CognitiveOS) — source of causal engine used in Routecast.

## Out of scope

- Training any LLM locally.
- Replacing RouterBench — the goal is to *extend* it with causal annotations.
- Claiming empirical dominance in F2; that comes in F3 (paper).

## Reproducibility checklist (enforced at F2.4)

- [ ] Commit hash pin for harness
- [ ] Seed documentation (`seed.yaml` per run)
- [ ] Environment snapshot (`pyproject.toml` + lock)
- [ ] Dataset version (DVC or hash-based)
- [ ] Hardware metadata in run artifacts
