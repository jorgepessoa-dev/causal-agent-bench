# Release Checklist: causal-agent-bench (F3.1–F3.2 Roadmap)

**Status**: Feature-complete for F3.1. Ready for publication + community adoption.  
**Date**: 2026-04-25  
**Owner**: Jorge (causal-agent-bench maintainer)

---

## Phase 1: Publication (NOW — arXiv + Benchmark Release)

### ✅ Completed

- [x] **F3.1 Paper**: 750 lines, 8 sections, 18 citations, sensitivity-analyzed (ADR-003 approved)
- [x] **Phase 3 DR-OPE Validation**: 5-seed synthetic grid, Thompson σ=0.005, gate assessment complete
- [x] **Phase 4 Gating Protocol**: Tier 1 PASS, Tier 2 roadmap documented
- [x] **Code**: Public repo (Apache-2.0), 15 test modules, CI determinism enforced
- [x] **Baselines**: 5 reference routers (random, heuristic, popularity, thompson, contextual_thompson)
- [x] **Package**: `pyproject.toml` configured, requires-python ≥3.10, metadata complete
- [x] **Documentation**: README updated (publication status), SUBMITTING guide, METRICS, RESULTS
- [x] **Governance**: ADR-003 signed, sensitivity analysis complete

### ⏳ Awaiting Jorge Authorization

- [ ] **Author Metadata**: Name, affiliation, email → add to F3.1 paper header
- [ ] **arXiv Submission**: Convert to PDF (pandoc) + upload to arXiv.org
- [ ] **arXiv ID Recording**: Log submission ID in `docs/SUBMISSION-LOG.md`

**Time to complete**: ~30 minutes  
**Blocker resolution**: Jorge action items in `docs/UPLOAD-CHECKLIST.md`

---

## Phase 2: Community Adoption (Post-Publication)

### Ready to Deploy

- [x] **PyPI Package**: `causal-agent-bench` v0.0.6 ready
  - Metadata: name, version, description, authors, license, classifiers
  - Dependencies: numpy ≥1.26, pandas ≥2.0, pydantic ≥2.0
  - Optional: dev (pytest, ruff, mypy), routers (placeholder)
  - **Next**: `python3 -m pip install causal-agent-bench` once published

- [x] **GitHub Leaderboard Service**: Ready to expand
  - CI: GitHub Actions on every commit
  - Determinism: byte-identical output enforcement
  - Fixtures: 500-row synthetic (regeneratable via `scripts/generate_synthetic_fixture.py`)
  - **Next**: Add web dashboard visualization (GitHub Pages / Streamlit optional)

- [x] **Community Submission Protocol**: SUBMITTING.md documented
  - Requirements: Protocol conformance, determinism, no network, tests, Apache-2.0 license
  - Process: PR against main, add router to `src/causal_agent_bench/routers/`
  - Ranking: quality (primary), coverage (tiebreak), name (deterministic tiebreak)
  - **Next**: Publicize on arXiv, announce in GitHub discussions

---

## Phase 3: Real-Data Validation (Q2 2026, Blocked on Licensing)

### Critical Path

- [ ] **RouterBench License Clearance**: Awaiting upstream approval
  - Blocker: Dataset licensing (MIT confirmed, usage license TBC)
  - Timeline: Track in `docs/upstream_issue_draft.md`
  - Dependency: Real-data gate testing cannot start without this

### Tier 2 Gate Testing (Post-Licensing)

- [ ] **G-Reward-MAE**: Measure reward model MAE on matched real-data rows (target < 0.15)
  - Requires: Routecast integration with trained reward model
  - Blocker: Routecast PyPI publish (F3.2+)
  - Impact: Random router disagreement improvement (6.6% → ~2%)

- [ ] **G-Inter-Rater Agreement**: κ ≥ 0.7 on task_type and difficulty annotations
  - Requires: RouterBench annotations + inter-rater protocol
  - Timeline: Post-licensing, 1–2 week annotation sprint expected
  - Impact: Validates annotation reliability for causal inference

- [ ] **G-PropCov-Real**: Propensity coverage ≥ 60% on real data
  - Test: Measure π̂₀ > 0 coverage on annotated RouterBench rows
  - Target: Ensure sufficient IPS overlap for unbiased estimation
  - Impact: Confirms DR-OPE applicability to real data

- [ ] **G-Disagreement**: DR-OPE vs match-IPS < 5% on real data
  - Test: Compare metrics across all routers on real-data test set
  - Target: Validate that DR-OPE is well-calibrated (not dramatically different from observed)
  - Impact: Builds confidence in metric flip decision

### Metric Flip Decision (Post-Real-Data Validation)

- [ ] **IF all Tier 2 gates pass**: Promote DR-OPE to PRIMARY metric
  - Changes: `mean_quality` → `dr_quality` as ranking criterion
  - Fallback: Retain match-IPS as secondary metric for sanity check
  - Announcement: Paper addendum or separate short note

- [ ] **IF any Tier 2 gate fails**: Defer metric flip, investigate root causes
  - Example: If κ < 0.7 → conduct deeper inter-rater analysis
  - Example: If reward MAE > 0.15 → retrain Routecast on real data
  - Timeline: Post-investigation, Q3–Q4 2026 retry

---

## Phase 4: Ecosystem Integration (Q3–Q4 2026)

### Causal Baseline

- [ ] **Routecast PyPI Publish**: Release `routecast` with trained reference models
  - Blocker: Awaits causal-agent-bench real-data validation
  - Impact: Enables `causal-agent-router` baseline submission
  - Timeline: Q2–Q3 2026 (after real-data gates)

- [ ] **CognitiveOS Integration**: Wire Routecast propensity + reward model to core
  - Scope: M31 (RAG adapter) + M32+ (causal routing in production)
  - Timeline: Parallel with real-data validation (Phase 4)

### Leaderboard Service

- [ ] **Web Dashboard**: Visualize router rankings + historical trends
  - Tech: GitHub Pages (static) or Streamlit (dynamic) or FastAPI (scalable)
  - Features: Interactive tables, seed-by-seed drill-down, cost-quality Pareto plots
  - Timeline: Post-publication, nice-to-have (not critical path)

- [ ] **Automated Submission Processing**: Accept router PRs, run CI, auto-rank
  - Process: Contributor opens PR → CI runs leaderboard → bot posts results
  - Timeline: Post-publication, once community submissions begin

---

## Success Criteria

| Criterion | F3.1 Status | F3.2 Status | Responsibility |
|-----------|-------------|-------------|-----------------|
| **Paper published** | ⏳ Awaiting upload | — | Jorge (author) |
| **Code public + reproducible** | ✅ Done | ✅ Maintain | Repo maintainer |
| **Phase 3 validation documented** | ✅ Done | ✅ Linked from paper | Documentation |
| **Community submissions enabled** | ✅ Protocol ready | 📋 Publish guidelines | Community |
| **Real-data gates passing** | — | ⏳ Blocked on licensing | Awaiting RouterBench |
| **DR-OPE as primary metric** | — | ⏳ Post-real-data | Metric flip decision |
| **Tier 4 integration** | — | 📋 Parallel work | CognitiveOS core |

---

## Risks & Mitigations

| Risk | Impact | Mitigation | Status |
|------|--------|-----------|--------|
| **RouterBench licensing blocked indefinitely** | Can't validate on real data; benchmark remains synthetic-only | Plan alternative dataset (synthetic expansion or synthetic-to-real transfer); publish findings on synthetic-only validity | 🟡 Tracked; escalate if >3 months |
| **Reward model quality < 0.15 MAE** | DR-OPE remains biased; metric flip deferred | Retrain on real data; integrate learned reward model (not dummy) | 🟢 Expected with Routecast integration |
| **Inter-rater agreement κ < 0.7** | Annotations unreliable for causal adjustment; confounding unblockable | Refine annotation protocol; add adjudication round; consider subset of high-confidence rows | 🟡 Handled by gate; redesign if fails |
| **Community routers don't materialize** | Benchmark becomes single-repository; limited scientific impact | Publicize submission protocol heavily; offer to support first 2–3 external contributions | 🟢 Plan post-publication outreach |

---

## Action Items (Sorted by Urgency)

### Immediate (Next 24 hours)

1. **[Jorge]** Complete author metadata + authorize arXiv upload
   - Reference: `docs/UPLOAD-CHECKLIST.md` (Step 1)
   - Effort: 5 min
   - Blocker: arXiv submission sequence

2. **[Jorge]** Run pandoc conversion + verify PDF output
   - Reference: `docs/UPLOAD-CHECKLIST.md` (Step 2)
   - Effort: 10 min
   - Blocker: arXiv format validation

### Short-term (Next week)

3. **[Maintainer]** Upload to arXiv + record submission ID
   - Reference: `docs/UPLOAD-CHECKLIST.md` (Steps 3–4)
   - Effort: 15 min
   - Impact: Establishes public timestamp + enables workshop submission

4. **[Maintainer]** Update GitHub repo description + links with arXiv URL
   - Effort: 5 min
   - Impact: Drives traffic, establishes priority

5. **[Community]** Announce on social media / research channels (optional)
   - Effort: 10 min
   - Impact: Increases visibility among routing + causal ML communities

### Medium-term (Post-Publication)

6. **[Maintainer]** Monitor for community router submissions
   - Effort: 2h/week (code review + CI monitoring)
   - Impact: Validates benchmark extensibility

7. **[Jorge + Routecast team]** Check RouterBench licensing status weekly
   - Effort: 15 min/week
   - Impact: Unblocks Phase 4 real-data validation

8. **[Maintainer]** Prepare for metric flip decision (post-Tier 2 gates)
   - Effort: 5h (documentation + testing)
   - Impact: Enables DR-OPE as primary metric

---

## Files & Artifacts

### Publication Package
- `F3.1_paper_integrated.md` (CognitiveOS repo)
- `PHASE-3-VALIDATION-REPORT.md` (causal-agent-bench repo)
- `PHASE-4-GATING-PROTOCOL.md` (causal-agent-bench repo)
- `ARXIV-SUBMISSION-PACKET.md` (this repo, submission guide)
- `UPLOAD-CHECKLIST.md` (this repo, author action items)

### Release Package
- `README.md` (updated with publication status)
- `pyproject.toml` (v0.0.6, ready for PyPI)
- `src/causal_agent_bench/` (code, 15 test modules)
- `tests/fixtures/synthetic_router_decisions_large.jsonl` (500-row benchmark)
- `scripts/generate_synthetic_fixture.py` (reproducibility)

### Governance & Planning
- `docs/SUBMITTING.md` (community submission protocol)
- `docs/METRICS.md` (evaluation contract)
- `docs/RESULTS.md` (reference leaderboard)
- `docs/ROADMAP.md` (feature roadmap)
- `docs/upstream_issue_draft.md` (RouterBench licensing tracker)

---

## Timeline Summary

| Phase | Milestone | Target | Status |
|-------|-----------|--------|--------|
| **1 — Publication** | arXiv submission | 2026-04-26 | ⏳ Awaiting Jorge |
| | Workshop acceptance | ~2026-05-15 | ⏳ Dependent on submission |
| **2 — Adoption** | Community submissions open | 2026-05-01 | 📋 Planned post-publication |
| **3 — Real-data validation** | Tier 2 gates testing | ~2026-06-01 | 🟡 Blocked on RouterBench licensing |
| | Metric flip decision | ~2026-07-01 | 🟡 Post-Tier 2 gates |
| **4 — Integration** | Routecast PyPI release | ~2026-07-01 | 📋 Parallel with Phase 3 |
| | Causal baseline submission | ~2026-08-01 | 📋 Post-Routecast release |

---

**Owner**: Jorge (causal-agent-bench)  
**Last updated**: 2026-04-25  
**Next review**: Post-arXiv submission (2026-04-27)

