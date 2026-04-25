# arXiv Upload Checklist (Ready Now)

**Deadline**: 15 May 2026 (NeurIPS 2026 Workshop)  
**Days remaining**: 20 days  
**Status**: All technical work complete. Awaiting author completion.

---

## Pre-Upload (Complete Now)

- [ ] **Author details**
  - Name(s): ?
  - Affiliation(s): ?
  - Email: ?
  - Co-authors (if any): ?
  
  → Add to `F3.1_paper_integrated.md` header

- [ ] **Verify paper links**
  - References.bib complete? ✅ (167 entries)
  - All \cite{key} keys mapped? ✅ (18 citations)
  - Figures embedded? ✅ (PNG in data/)
  
- [ ] **Phase 3 validation linkage**
  - PHASE-3-VALIDATION-REPORT.md accessible? ✅
  - Gate assessment clear (Tier 1 PASS, Tier 2 pending)? ✅
  - DR-OPE formula validated? ✅
  
- [ ] **Supporting docs ready**
  - ADR-003 present? ✅
  - CAUSAL_ASSUMPTIONS.md prepared? ✅
  - Code repo public? ✅ (github.com/jorgepessoa-dev/causal-agent-bench)

---

## Upload Steps (Jorge Action Items)

### 1. Pandoc Conversion (5 min)
```bash
cd /home/jorge/projects/CognitiveOS/research/paper
pandoc F3.1_paper_integrated.md \
  --bibliography=references.bib \
  --from=markdown \
  --to=pdf \
  --output=causal-agent-bench_F3.1.pdf
```

### 2. Create arXiv Account (if needed)
Visit: https://arxiv.org/user/register

### 3. Upload to arXiv (15 min)
1. Go to https://arxiv.org/submit
2. **Title**: "causal-agent-bench: An Open Benchmark and Evaluation Protocol for Causal LLM Routing"
3. **Authors**: [Your name] (and co-authors if applicable)
4. **Affiliation**: [Your institution]
5. **Abstract**: Use paper abstract (or customize with Phase 3 highlight)
6. **Comments**: "Extended with Phase 3 DR-OPE validation report; 14 pages including supplementary results"
7. **Subjects**: 
   - Primary: `cs.LG` (Machine Learning)
   - Secondary: `cs.AI` (Artificial Intelligence)
8. **Files to upload**:
   - `causal-agent-bench_F3.1.pdf` (main paper)
   - `references.bib` (bibliography)
   - `PHASE-3-VALIDATION-REPORT.md` (supplementary results, as markdown or PDF)
   - `ADR-003-causal-agent-bench-public-release.md` (governance, optional)

### 4. Record Submission ID
Once uploaded, arXiv returns a submission ID (e.g., `2604.xxxxx`). Record in `docs/SUBMISSION-LOG.md`.

### 5. Announce Publication
- Update README: "Paper published on arXiv: [link]"
- Announce in code repository issues/discussions
- Post on social media / research channels (optional)

---

## Post-Upload (Immediate)

- [ ] **Verify arXiv listing** (appears within 24h)
- [ ] **Update repo docs** with arXiv link
- [ ] **Commit submission metadata** to git:
  ```bash
  git add docs/ARXIV-SUBMISSION-PACKET.md docs/UPLOAD-CHECKLIST.md
  git commit -m "docs(publication): F3.1 + Phase 3 validation arXiv submission packet ready"
  git push
  ```

---

## Success Criteria

✅ **Submitted**: Manuscript accepted by arXiv and assigned public ID  
✅ **Trackable**: Submission date logged and linked in repository  
✅ **Reproducible**: Phase 3 validation supports all causal claims  
✅ **Public**: Code + benchmark fully open-source (Apache-2.0)  

---

## Parallel Tasks (While Awaiting Upload Authorization)

If upload is delayed:

1. **Code release polish** — Ensure causal-agent-bench PyPI package is publication-ready
2. **Leaderboard service** — Set up web leaderboard (phase 2 roadmap item)
3. **Community submission protocol** — Document how third-party routers can submit to benchmark
4. **Real-data roadmap** — Prepare for Phase 4 once RouterBench licensing clears

---

**Time estimate for Steps 1–5**: ~30 minutes  
**Jorge authorization required**: Yes (author metadata, arXiv upload)  
**Ready to proceed**: ✅ Yes, awaiting Jorge signal

