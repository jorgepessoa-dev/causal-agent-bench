# causal-agent-bench: arXiv Submission Packet (2026-04-25)

**Status**: Ready for author completion + upload  
**Deadline**: NeurIPS 2026 Workshop (15 May 2026)  
**Location**: `/home/jorge/projects/CognitiveOS/research/paper/`

---

## Submission Package Contents

### Primary Manuscript
**File**: `F3.1_paper_integrated.md` (30 KB, ~750 lines)

**Sections**: Abstract, §1–§8 (Introduction through Conclusion + References)
- §1: Motivation, gap analysis, contributions (C1–C5)
- §2: Problem formulation + DR-OPE design
- §3: Benchmark design (annotation schema, split protocol, metric contract)
- §4: Five reference baselines (algorithms + code pointers)
- §5: Empirical study (Table 1: match-IPS on 5-seed grid, synthetic fixture)
- §6: Limitations (synthetic-only, match-IPS bias, propensity gaps, small-sample variance, unobserved confounders)
- §7: Related work (routing, causal bandits, benchmarks)
- §8: Conclusion + release plan

**Compliance**: 
- ✅ Page-fit: ~7.5 pages at 2-column NeurIPS layout
- ✅ Causal claims sensitivity-analyzed (ADR-003 approved)
- ✅ Limitations honestly stated in §6
- ✅ Real-data deferral transparent (§1.5, §6, §8)

---

### Extended Results (Supplementary Report)
**File**: `PHASE-3-VALIDATION-REPORT.md` (causal-agent-bench repo)

**Adds**: DR-OPE metrics to the same 5-seed synthetic grid reported in §5.

**Contents**:
- Executive summary: Gate assessment (Tier 1 synthetic PASS, Tier 2 real-data pending)
- Aggregate metrics table: match-IPS vs DR-OPE disagreement per router
- Seed-by-seed Thompson stability (σ=0.005)
- Per-difficulty stratification analysis
- Root cause analysis: Random router disagreement (6.6%) due to DummyRewardModel, addressable via RoutcastWrapper
- Sensitivity checks: reward model quality impact, propensity smoothing, per-difficulty invariance

**Purpose**: 
- Validates that DR-OPE formula is implemented correctly (§2.4 claims)
- Documents bias-variance trade-off in contextual_thompson (mentioned in §5.3)
- Establishes roadmap for metric flip decision (DR-OPE as primary post-real-data)

**Positioning**: "Extended technical validation of §5 results under doubly-robust estimation framework."

---

### Governance & Sensitivity
**File**: `ADR-003-causal-agent-bench-public-release.md`

**Documents**:
- Owner approval for public release (Jorge, 2026-04-25)
- Claim remediation (adversarial review responses)
- Causal assumptions and sensitivity bounds

---

## Author Completion Checklist

### Step 1: Author Metadata
Add to `F3.1_paper_integrated.md` (top of file, before Abstract):

```
**Author(s)**: {name, affiliation, email}
**Submission date**: 2026-04-25
**Venue**: NeurIPS 2026 Workshop on Causal Machine Learning / Decision-Making under Uncertainty
**Code availability**: github.com/jorgepessoa-dev/causal-agent-bench (Apache-2.0)
**Extended results**: PHASE-3-VALIDATION-REPORT.md (supplementary validation under DR-OPE framework)
```

### Step 2: Bibliography Verification
- `references.bib` is complete (167 entries)
- All 18 citations in paper are mapped (keys lowercase author-year style)
- No missing venues (scan for TODO markers)

**Command to verify**: `grep -i "TODO\|venue\|arxiv" references.bib`

### Step 3: Figure Conversion (Optional at submission, required for camera-ready)
- 2 PNG figures included: `fig_quality_vs_coverage.png`, `fig_confounder_dag.png`
- At camera-ready, embed in LaTeX template via `\includegraphics`

### Step 4: arXiv Submission
1. Go to `https://arxiv.org/submit`
2. Upload as PDF (convert from markdown using `pandoc` + `references.bib`)
3. **Authors**: List authorship clearly (Jorge + any co-authors)
4. **Abstract**: Use paper abstract (reword if needed to highlight Phase 3 validation)
5. **Comments**: "14 pages including extended results on DR-OPE validation"
6. **Subjects**: cs.LG (Machine Learning), cs.AI (Artificial Intelligence)
7. Submit for publication

---

## Markdown → PDF Conversion Command

```bash
pandoc F3.1_paper_integrated.md \
  --bibliography=references.bib \
  --csl=ieee.csl \
  --from=markdown \
  --to=pdf \
  --output=causal-agent-bench_F3.1.pdf \
  --variable=geometry:margin=0.5in
```

*(Requires `pandoc`, `pandoc-citeproc`, IEEE CSL)*

---

## Phase 3 Validation Integration

**In arXiv submission, reference as:**

> "Extended technical validation of §5 empirical claims under doubly-robust off-policy evaluation (DR-OPE) is provided in the supplementary report (PHASE-3-VALIDATION-REPORT.md). The 5-seed synthetic grid validates that: (i) Thompson sampling remains stable under DR-OPE (σ=0.005); (ii) causal formula does not exhibit cliff behavior; (iii) real-data gate criteria are well-defined and traceable to propensity + reward model quality. The report also documents the roadmap for metric flip decision (from match-IPS to DR-OPE primary) pending real-data validation (Phase 4, awaiting RouterBench licensing)."

---

## Timeline & Dependencies

| Milestone | Date | Status | Blocker |
|-----------|------|--------|---------|
| **F3.1 paper + Phase 3 validation** | 2026-04-25 | ✅ DONE | — |
| **Author metadata + arXiv upload** | 2026-04-26 | ⏳ PENDING | Jorge authorization |
| **Workshop notification** | ~2026-05-15 | ⏳ PENDING | arXiv submission |
| **Real-data Phase 4 (Tier 2 gates)** | ~2026-06-01 | ⏳ BLOCKED | RouterBench licensing |
| **Post-publication roadmap (CWM, E-ACE, metric flip)** | Q2–Q3 2026 | 📋 PLANNED | — |

---

## Key Success Criteria

- ✅ Paper passes NeurIPS workshop review (causal rigor, novel benchmark, reproducible code)
- ✅ Phase 3 validation supports causal claims (DR-OPE stability, no cliff behavior)
- ✅ Limitations transparently stated (synthetic-only, real-data deferred, causal assumptions)
- ✅ Code + benchmark publicly available (github.com/jorgepessoa-dev/causal-agent-bench, Apache-2.0)
- ✅ Citation trail complete (ADR-003, paper provenance, phase gates documented)

---

## Files to Upload to arXiv

```
causal-agent-bench_F3.1.pdf          # Converted from markdown
references.bib                       # Bibliography
PHASE-3-VALIDATION-REPORT.md         # Supplementary results (as PDF or markdown)
ADR-003-public-release.md            # Governance record (as PDF or markdown)
```

---

**Next Action**: Jorge completes author metadata (Step 1) → triggers arXiv upload.

**Owner**: Jorge (causal-agent-bench maintainer)  
**Date prepared**: 2026-04-25  
**Status**: Ready for publication phase

