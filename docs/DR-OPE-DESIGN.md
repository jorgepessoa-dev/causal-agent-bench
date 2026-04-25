# G-DR-OPE-v1: Design Document (Phase 1)

**Date**: 2026-04-25  
**Status**: DESIGN (Phase 1/4)  
**Goal**: Audit Routecast integration; design DR-OPE validation protocol

---

## Current State (F3.1)

### Evaluation Harness
- **File**: `src/causal_agent_bench/evaluation.py`
- **Current metric**: match-IPS only
  - Line 97: Counts only rows where `router.choice == log.choice`
  - Line 98-101: Uses observed quality/cost from log
  - Result: `mean_quality = sum(q_i | match_i=1) / n_matches`
- **Coverage metric**: Honest audit of match rate (prevents gaming via narrow domain)

### Router Protocol
- **File**: `src/causal_agent_bench/router.py`
- **RouterChoice** schema:
  - `selected_model: str` (required)
  - `propensity: Optional[float]` (optional, for OPE)
  - Only `random` router populates propensity (= 1/|candidates|)
  - All others: propensity = None

### Missing Pieces (for DR-OPE)
1. **Propensity estimator** — where to get $\hat{\pi}_0(a \mid x, e)$?
   - Paper §2.4: "annotation-conditioned empirical distribution $\hat{\pi}_0(a \mid \text{task_type}, \text{difficulty})$ plus Dirichlet smoother"
   - Not yet implemented in evaluation harness
2. **Reward model** — where to get $\hat{q}(x, a)$?
   - Paper §2.4: "supplied by a reference causal router — the paper uses **Routecast**"
   - Routecast not yet integrated into leaderboard
3. **DR-OPE formula** — not in `evaluation.py`
   - Formula: $\widehat{V}_{\text{DR}}(\pi) = \frac{1}{n}\sum_i \left[ \hat{q}(x_i, \pi(x_i)) + \frac{\mathbb{1}[\pi(x_i) = a_i]}{\hat{\pi}_0(a_i \mid x_i)}(q_i - \hat{q}(x_i, a_i)) \right]$

---

## Design: DR-OPE-v1 Integration

### Architecture

```
┌─ Evaluation Harness (evaluation.py)
│
├─ Match-IPS (current)
│  └─ Output: mean_quality (over matches only)
│
├─ NEW: DR-OPE (feature-gated)
│  ├─ Propensity estimator
│  │  └─ Source: Annotation-conditioned empirical dist
│  │         (task_type, difficulty stratification)
│  │
│  ├─ Reward model
│  │  └─ Source: Routecast.predict_quality(x, a)
│  │         OR: reference SCM from causal-agent-bench
│  │
│  └─ Output: dr_quality (full formula)
│
└─ Report (leaderboard.py)
   ├─ mean_quality (match-IPS, PRIMARY at F3.1)
   ├─ dr_quality (feature-gated, validation at F3.1)
   └─ (metric flip to DR-OPE post-real-data validation)
```

### Implementation Sketch

**File**: `src/causal_agent_bench/evaluation.py` (extend)

```python
def evaluate_router_with_dr_ope(
    router: Router,
    source: DataSource,
    propensity_estimator: Optional[PropensityEstimator] = None,
    reward_model: Optional[RewardModel] = None,
    use_dr_ope: bool = False,  # Feature flag
) -> EvaluationReport:
    """
    Compute match-IPS + optional DR-OPE.
    
    Args:
        propensity_estimator: Callable[[x, e, a] -> float]
            Estimate π₀(a | x, e). If None, DR-OPE uses annotation-conditional empirical.
        reward_model: Callable[[x, a] -> float]
            Estimate q(x, a). If None, DR-OPE uses Routecast.predict_quality(x, a).
        use_dr_ope: If True, compute both match-IPS and DR-OPE. Report both.
    """
    # Existing match-IPS logic (unchanged)
    match_ips_result = ... # EvaluationReport
    
    # NEW: DR-OPE if requested
    if use_dr_ope:
        propensity_est = propensity_estimator or AnnotationConditionedEmpirical(source)
        reward_est = reward_model or RoutcastWrapper()
        
        dr_ope_result = _compute_dr_ope(
            router, source, propensity_est, reward_est
        )
        # Merge results: return both metrics
        return EvaluationReport(
            n_rows=...,
            n_matches=...,
            mean_quality=match_ips_result.mean_quality,  # Match-IPS (primary)
            dr_quality=dr_ope_result.mean_quality,       # DR-OPE (validation)
            ... per_difficulty for both ...
        )
    
    return match_ips_result
```

### Propensity Estimator

**Source**: Annotation-conditioned empirical distribution

```python
class AnnotationConditionedEmpirical:
    """π₀(a | task_type, difficulty) from warmup data."""
    
    def __init__(self, warmup_decisions: List[AnnotatedDecision]):
        # Build contingency table: (task_type, difficulty, model) -> count
        self.counts = {}  # (task, diff, model) -> int
        self.totals = {}  # (task, diff) -> int
        for ad in warmup_decisions:
            key = (ad.annotation.task_type, ad.annotation.difficulty)
            model_key = (key, ad.decision.selected_model)
            self.counts[model_key] = self.counts.get(model_key, 0) + 1
            self.totals[key] = self.totals.get(key, 0) + 1
    
    def estimate(self, task_type: str, difficulty: str, model: str) -> float:
        """Estimate π₀(model | task_type, difficulty)."""
        key = (task_type, difficulty)
        total = self.totals.get(key, 0)
        if total == 0:
            return 1.0 / len(available_models)  # Uniform fallback
        count = self.counts.get((key, model), 0)
        # Dirichlet smoother (α=1 for now; tune later)
        alpha = 1.0
        return (count + alpha) / (total + alpha * len(models))
```

### Reward Model

**Source**: Routecast (or fallback to reference SCM)

```python
class RoutcastWrapper:
    """Wrapper around Routecast.predict_quality(x, a)."""
    
    def __init__(self, routecast_instance=None):
        # If None, lazy-load from pip install routecast
        self.routecast = routecast_instance or load_routecast()
    
    def predict(self, decision: RouterDecision, model: str) -> float:
        """Estimate q(x, model) using Routecast's posterior mean."""
        return self.routecast.predict_quality(
            prompt=decision.prompt,
            model=model,
            annotation=decision.annotation
        )
```

### DR-OPE Formula

```python
def _compute_dr_ope(
    router: Router,
    source: DataSource,
    propensity_est: PropensityEstimator,
    reward_est: RewardModel,
) -> float:
    """
    Compute: V_DR = (1/n) * Σ [
        q̂(x_i, π(x_i)) +
        𝟙[π(x_i) = a_i] / π̂₀(a_i | x_i) * (q_i - q̂(x_i, a_i))
    ]
    """
    dr_terms = []
    
    for ad in source:
        x, a_log = ad.decision, ad.decision.selected_model
        a_eval = router.route(ad.decision, ad.annotation).selected_model
        q_log = ad.decision.observed_quality
        
        # First term: direct method
        q_pred_eval = reward_est.predict(ad.decision, a_eval)
        
        # Second term: IPS correction (only if match)
        ips_term = 0.0
        if a_eval == a_log:
            propensity = propensity_est.estimate(
                ad.annotation.task_type,
                ad.annotation.difficulty,
                a_log
            )
            if propensity > 0:  # Avoid division by zero
                q_pred_log = reward_est.predict(ad.decision, a_log)
                ips_term = (q_log - q_pred_log) / propensity
        
        dr_terms.append(q_pred_eval + ips_term)
    
    return sum(dr_terms) / len(dr_terms) if dr_terms else 0.0
```

---

## Validation Protocol (Phase 3)

### Research Question
**When does DR-OPE help over match-IPS? When does it hurt?**

### Experiment
- **Dataset**: Synthetic fixture (500 rows), 5-seed grid
- **Baselines**: All 5 routers (random, heuristic, popularity, thompson, contextual_thompson)
- **Metrics**:
  - `match_ips_quality` (current)
  - `dr_ope_quality` (new)
  - `dr_ips_disagreement` = |dr - match| / match (%)
  - `propensity_coverage` = fraction of rows with π̂₀ > 0
  - `reward_model_mae` = mean absolute error of q̂(x, a) vs observed q (on matches)

### Expected Outcomes

| Router | match-IPS | DR-OPE | Disagreement | Explanation |
|--------|-----------|--------|--------------|-------------|
| `random` | ✓ baseline | ✓ should match | <5% | π₀ known exactly (1/|A|); no propensity bias |
| `thompson` | high (0.826) | ≈ match-IPS | <10% | Propensity gap (β-posterior); dr corrects if q̂ good |
| `contextual_thompson` | ≈ match-IPS | high | >20% | Coverage low; DR inflates due to 1/π̂₀ scaling |
| `heuristic` | high (0.815) | N/A | deterministic | No propensity; DR-IPS undefined |

### Success Criteria
- [ ] Random router: DR-OPE ≈ match-IPS (within 2%)
- [ ] Thompson: DR-OPE stable across seeds (σ ≤ 0.02)
- [ ] Propensity coverage > 50% across all routers
- [ ] Reward model MAE < 0.15 on matched rows
- [ ] No "cliff" where DR-OPE becomes unstable (e.g., due to π̂₀ → 0)

---

## Deliverables (Phase 1/4)

- [x] Audit current evaluation harness (match-IPS only)
- [x] Identify propensity source (annotation-conditioned empirical)
- [x] Identify reward model source (Routecast wrapper)
- [x] Design DR-OPE formula integration
- [x] Draft validation protocol (experiment design + success criteria)
- [ ] **NEXT**: Implement propensity estimator class
- [ ] **NEXT**: Implement Routecast wrapper
- [ ] **NEXT**: Integrate DR-OPE into evaluation.py
- [ ] **NEXT**: Run 5-seed validation on synthetic fixture

---

## Open Questions (for Phase 2 review)

1. **Dirichlet smoother**: Should α=1 (uniform prior) or data-driven?
2. **Propensity fallback**: When π̂₀ = 0 (unobserved (task,diff,model)), use uniform or ignore row?
3. **Reward model source**: 
   - Option A: Routecast (external pip install; adds dependency)
   - Option B: Reference SCM (self-contained; slower to compute)
   - Option C: Pluggable (user provides at eval time)
4. **Feature flag naming**: `--use-dr-ope` or `--metric match-ips|dr-ope|both`?
5. **Real-data gate**: Minimum propensity coverage / reward MAE before flipping metric from match-IPS to DR-OPE?

---

## Timeline

- **Week 1 (now)**: Design audit + phase 1 ✓ (this doc)
- **Week 2**: Implementation (propensity + reward model + formula)
- **Week 3**: Validation (5-seed synthetic grid + analysis)
- **Week 4**: Documentation + real-data gate definition

