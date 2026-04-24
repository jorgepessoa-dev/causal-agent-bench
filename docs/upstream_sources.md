# Upstream dataset sources

Status: F2.2 preparation — license due-diligence before data ingestion.

## RouterBench (primary upstream)

- **Paper**: Hu et al., "RouterBench: A Benchmark for Multi-LLM Routing System" — arXiv:2403.12031 (2024).
- **Dataset size**: 405k routing outcomes across 11 LLMs, 8 benchmarks.
- **Upstream code repo**: `withmartian/routerbench` on GitHub. **License: MIT** ([verified 2026-04-24 via `gh api repos/withmartian/routerbench`](https://github.com/withmartian/routerbench/blob/main/LICENSE)).
- **Upstream dataset repo**: `withmartian/routerbench` on HuggingFace Hub (`routerbench_0shot.pkl`, `routerbench_5shot.pkl`, `routerbench_raw.pkl`; ~1.47 GB; 30k+ prompts × 11 LLMs).
- **Dataset license**: **⚠️ ABSENT** on the HF dataset card ([verified 2026-04-24 via `GET https://huggingface.co/api/datasets/withmartian/routerbench`](https://huggingface.co/api/datasets/withmartian/routerbench) — no `license` field in metadata; README on the dataset page has no license tag either). This is a **hard blocker** for F2.2 ingestion.
- **Attribution**: arXiv:2403.12031 citation required regardless.

### Compatibility checklist

- [x] Code repo license read: **MIT** (compatible with our Apache-2.0 distribution)
- [ ] **BLOCKED** — Dataset license absent on HF. Resolution options before ingestion:
      (a) open a GitHub issue on `withmartian/routerbench` asking for explicit dataset-card license,
      (b) email paper authors via arXiv contact info,
      (c) ingest only the code-repo-bundled test fixtures (if any), or
      (d) fall back to **LMRouter** / our synthetic fixture.
      **Do not ingest the HF pickles until (a)/(b) resolves or until the owner signs a risk-accepted ADR.**
- [ ] License text saved to `datasets/routerbench/LICENSE.upstream` (pending)
- [ ] Redistribution clause verified — pending license clarification
- [ ] Attribution template written in `datasets/routerbench/README.md` (pending)

### Schema mapping (RouterBench → our schema)

Per RouterBench v1 (confirm column names at ingestion):

| RouterBench column | our `RouterDecision` field | transform |
|---|---|---|
| `sample_id` | `decision_id` | direct |
| `prompt` | `prompt` | direct |
| `model` (winning) | `selected_model` | direct |
| `models` (candidates) | `candidate_models` | direct |
| `cost` | `observed_cost` | direct (USD) |
| `correct` (0/1) or `score` | `observed_quality` | cast to float [0,1] |
| `router` (if present) | extra field (via `extra="allow"`) | passthrough |

Annotation columns (`CausalAnnotation`) are **added by us**, not upstream:
- `task_type`: inferred by LLM annotator (Haiku 4.5, configurable) from `prompt`
- `difficulty`: inferred similarly
- `confounders`: optional domain tags
- `annotator_id`: string identifying the annotator run
- `confidence`: annotator self-reported

## Alternative upstreams (fallback if RouterBench license is restrictive)

- **LMRouter** (MIT) — smaller (~50k), but clean license.
- **Synthetic fixture** (ours) — `tests/fixtures/synthetic_router_decisions.jsonl`, unrestricted.

## Decision log

- 2026-04-24: Stub created; ingestion deferred to the dedicated F2.2 session (license verification is a real prerequisite, not a speed-bump).
- 2026-04-24 (later): Upstream license audit performed. Code repo = MIT ✅. Dataset card = license absent ❌. **F2.2 ingestion remains blocked.** Owner action required: pick between (a) upstream clarification request, (b) fallback to LMRouter/synthetic, or (c) signed risk-accept ADR. Recommend (a) first — low cost, clean outcome if resolved.
