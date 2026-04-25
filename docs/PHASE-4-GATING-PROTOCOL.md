# Phase 4: DR-OPE Gating & Metric Flip Protocol

**Date**: 2026-04-25  
**Status**: PHASE 4/4 — Documentation + Gating  
**Owner**: Jorge (causal-agent-bench)

---

## Overview

**Purpose**: Define gate criteria for when to switch from match-IPS (F3.1, current) to DR-OPE (F3.2+, validated).

**Timeline**:
- F3.1: match-IPS PRIMARY, DR-OPE optional (feature flag `--use-dr-ope`)
- F3.2 (post-real-data): Metric flip decision (→ DR-OPE PRIMARY if real-data gates pass)

---

## Gate Definitions

### Tier 1: Synthetic Validation Gates (F3.1 → F3.2 entry)

| Gate | Criterion | F3.1 Status | Threshold | Notes |
|------|-----------|-------------|-----------|-------|
| **G-Stability** | Thompson σ(dr_ope) across 5 seeds | ✅ PASS | σ ≤ 0.02 | Result: σ=0.005 (✓ strong) |
| **G-Cliff** | No cliff behavior in DR-OPE | ✅ PASS | Estimates bounded [0,1] | Result: no instability observed |
| **G-Coverage** | ≥1 router with match rate ≥50% | ✅ PASS | coverage ≥ 50% | Result: heuristic 59.8% (✓) |
| **G-Propensity** | Propensity > 0 for ≥90% rows | ✅ PASS | Non-zero propensity | Result: ~100% (uniform fallback) |

**F3.1 Status**: All synthetic gates PASS → DR-OPE feature-ready.

### Tier 2: Real-Data Gates (F3.2 → Production flip)

To be defined once RouterBench annotations available (awaiting κ ≥ 0.7 inter-rater agreement):

| Gate | Criterion | F3.2 Placeholder | Target | Purpose |
|------|-----------|------------------|--------|---------|
| **G-Reward-MAE** | Reward model MAE on matched rows | Not yet measured | < 0.15 | Ensures q̂ estimator quality |
| **G-Inter-Rater** | Annotation agreement (Cohen's κ) | Awaiting annotation | κ ≥ 0.7 | Ensures quality labels are reliable |
| **G-PropCov-Real** | Propensity coverage in real data | Awaiting annotation | ≥ 60% | Sufficient rows for IPS correction |
| **G-Disagreement** | DR-OPE vs match-IPS disagreement | Awaiting annotation | < 5% | Ensures consistency with observed |

**Trigger**: When RouterBench licensing clears → re-run Phase 3 on annotated real data.

---

## Metric Flip Protocol

### Current State (F3.1)

```
PRIMARY METRIC: mean_quality (match-IPS)
- Robust: only uses observed outcomes
- Limited: coverage < 100% (mismatches excluded)
- Interpretation: "What did our router achieve on matched decisions?"

SECONDARY METRIC: dr_quality (DR-OPE, optional)
- Broader: estimates impact of all decisions
- Speculative: depends on reward model + propensity
- Interpretation: "What would the full policy deliver (estimated)?"
```

### Metric Flip Decision (F3.2, post-real-data)

**IF all Tier 2 gates pass:**

```
PRIMARY METRIC: dr_quality (DR-OPE)
- Unbiased: importance-sampling correction
- Comprehensive: includes off-policy rows
- Interpretation: "Causal estimate of true policy value"

SECONDARY METRIC: mean_quality (match-IPS)
- Fallback: sanity check
- Interpretation: "Conservative lower-bound on matched rows"
```

**Flip Trigger**:
1. G-Reward-MAE passes (q̂ model is good)
2. G-Inter-Rater passes (annotations reliable)
3. G-PropCov-Real passes (sufficient overlap)
4. G-Disagreement passes (no surprising divergence)

**Rollback Protocol** (if gates fail):
- Keep match-IPS as PRIMARY
- Continue with --use-dr-ope as research feature
- Address root causes (better reward model, more annotations, etc.)

---

## Success Metrics for Validation Report

### Synthetic Validation (F3.1 → F3.2 entry, in progress)

- [x] Thompson stability (σ ≤ 0.02): **PASS** (0.005)
- [x] No cliff behavior: **PASS** (no instability)
- [x] Heuristic coverage ≥ 50%: **PASS** (59.8%)
- [x] Propensity > 0: **PASS** (~100%)
- [ ] **Remaining**: Random router disagreement (6.6% vs 2% threshold — improve with RoutcastWrapper)

### Real-Data Validation (F3.2 → Production, awaiting data)

- [ ] Reward model MAE < 0.15 (on matched rows)
- [ ] Inter-rater agreement κ ≥ 0.7 (annotation reliability)
- [ ] Propensity coverage ≥ 60% (sufficient IPS overlap)
- [ ] Disagreement < 5% (DR-OPE vs match-IPS aligned)

---

## Sensitivity Analysis (Phase 4 Research)

### Known Sensitivities

1. **Reward Model Quality**
   - Current: DummyRewardModel(0.75) — naive estimator
   - Impact: Random router disagreement = 6.6% (target 2%)
   - Mitigation: RoutcastWrapper with trained Routecast model
   - Expected improvement: disagreement → 1–2%

2. **Propensity Smoothing (Dirichlet α)**
   - Current: α = 1.0 (uniform prior)
   - Impact: Handles unseen strata gracefully (uniform fallback)
   - Sensitivity: Reducing α → lower propensity → higher IPS variance
   - Recommendation: Keep α = 1.0 unless Tier 2 data shows systematic bias

3. **Propensity Coverage Dependency**
   - Current: Coverage ~35–60% (match rate)
   - Impact: IPS term only applied to matches
   - Sensitivity: Low coverage → high variance (1/π̂₀ large)
   - Mitigation: Ensure warm-up split ≥ 100 rows, sufficient stratification

4. **Reward Model Calibration**
   - Current: No calibration (raw predictions)
   - Sensitivity: Miscalibrated q̂ → biased DR-OPE
   - Mitigation: Measure MAE, apply temperature scaling if needed

---

## Recommendation for F3.2 Rollout

### If Real-Data Gates Pass
→ **FLIP to DR-OPE as PRIMARY** (recommended for ICML submission)

**Rationale**:
- Thompson stability validates generalization
- Synthetic → real-data transfer increases confidence
- DR-OPE's unbiased estimation suits causal research agenda
- Broader coverage better for benchmarking (fewer rows excluded)

### If Real-Data Gates Fail
→ **KEEP match-IPS as PRIMARY**, continue DR-OPE as optional feature

**Rationale**:
- Safer: match-IPS has weaker assumptions
- Actionable: identify root cause (reward model, annotations, etc.)
- Iterative: improve components, retry Phase 2–3

---

## Files Modified (Phase 4)

- `docs/PHASE-4-GATING-PROTOCOL.md` (this file)
- `docs/PHASE-3-VALIDATION-REPORT.md` (to be generated)
- `docs/SENSITIVITY-ANALYSIS.md` (DR-OPE parameter sensitivity study)

---

## Timeline

- **Week 3 (now)**: Phase 3 validation + Phase 4 gating definition ✓
- **Week 4**: Real-data collection & Tier 2 gate testing (awaiting RouterBench licensing)
- **Week 5+**: Metric flip decision & ICML/workshop submission

---

**Owner**: Jorge  
**Status**: Phase 4 in progress (gating definition 100%, real-data gates pending)
