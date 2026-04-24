# Upstream dataset sources

Status: F2.2 preparation — license due-diligence before data ingestion.

## RouterBench (primary upstream)

- **Paper**: Hu et al., "RouterBench: A Benchmark for Multi-LLM Routing System" — arXiv:2403.12031 (2024).
- **Dataset size**: 405k routing outcomes across 11 LLMs, 8 benchmarks.
- **Upstream repo**: `withmartian/routerbench` on HuggingFace Hub.
- **License**: **CONFIRM BEFORE INGESTION**. Check HF dataset card `license` field. Expected MIT / CC-BY / Apache-2.0 (compatible with our Apache-2.0). If GPL / non-commercial, STOP and pick different source.
- **Attribution**: required in `datasets/routerbench/README.md` + our paper's "Data" section.

### Compatibility checklist

- [ ] License field read from HF dataset card (not just repo metadata)
- [ ] License text saved to `datasets/routerbench/LICENSE.upstream`
- [ ] Redistribution clause verified — does the license allow hosting derived/annotated subsets?
- [ ] Attribution template written in `datasets/routerbench/README.md`

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
