# Submission Log: causal-agent-bench (arXiv + Workshop)

## F3.1 Paper + Phase 3 Validation

**Author**: Jorge Pessoa  
**Affiliation**: Independent  
**Email**: jorge.pessoa.mail@gmail.com  
**Paper location**: `/home/jorge/projects/CognitiveOS/research/paper/F3.1_paper_integrated.md`  
**Validation report**: `/home/jorge/projects/causal-agent-bench/docs/PHASE-3-VALIDATION-REPORT.md`  

---

## arXiv Submission (Awaiting Upload)

| Field | Value | Status |
|-------|-------|--------|
| **Title** | causal-agent-bench: An Open Benchmark and Evaluation Protocol for Causal LLM Routing | ✅ Ready |
| **Abstract** | [From paper §Abstract] | ✅ Ready |
| **Authors** | Jorge Pessoa (Independent) | ✅ Ready |
| **Subjects** | cs.LG, cs.AI | ✅ Ready |
| **Comments** | Extended with Phase 3 DR-OPE validation report; 14 pages including supplementary results | ✅ Ready |
| **PDF file** | causal-agent-bench_F3.1.pdf | ⏳ Await pandoc |
| **Bibliography** | references.bib (167 entries) | ✅ Ready |
| **arXiv ID** | [To be assigned] | ⏳ Pending upload |
| **Submission date** | 2026-04-25 (preparation) | ✅ Ready |
| **Target date** | 2026-04-26 (upload) | ⏳ Pending |

---

## Upload Checklist (TODO)

- [ ] **Step 1**: Verify author metadata in paper (added 2026-04-25)
  ```
  Author(s): Jorge Pessoa
  Affiliation: Independent
  Email: jorge.pessoa.mail@gmail.com
  ```

- [ ] **Step 2**: Convert to PDF using pandoc
  ```bash
  cd /home/jorge/projects/CognitiveOS/research/paper
  pandoc F3.1_paper_integrated.md \
    --bibliography=references.bib \
    --from=markdown \
    --to=pdf \
    --output=causal-agent-bench_F3.1.pdf
  ```

- [ ] **Step 3**: Create arXiv account (if needed)
  - Visit: https://arxiv.org/user/register

- [ ] **Step 4**: Upload to arXiv
  - Go to: https://arxiv.org/submit
  - Title: causal-agent-bench: An Open Benchmark and Evaluation Protocol for Causal LLM Routing
  - Authors: Jorge Pessoa
  - Affiliation: Independent
  - Abstract: [From paper]
  - Comments: Extended with Phase 3 DR-OPE validation report; 14 pages including supplementary results
  - Subjects: cs.LG (primary), cs.AI (secondary)
  - Files:
    - causal-agent-bench_F3.1.pdf
    - references.bib
    - PHASE-3-VALIDATION-REPORT.md (optional, as supplementary)

- [ ] **Step 5**: Record submission details
  ```
  arXiv ID: [assigned by arXiv]
  Submission URL: https://arxiv.org/abs/[ID]
  Submission date: [date confirmed]
  Status: [submitted | posted]
  ```

---

## Post-Submission

- [ ] **Verify arXiv listing** (appears within 24h)
  - Expected URL: `https://arxiv.org/abs/YYMM.XXXXX`
  - Check: Title, authors, abstract, PDF rendering

- [ ] **Update repository**
  ```bash
  cd /home/jorge/projects/causal-agent-bench
  # Update README.md with arXiv URL
  git add docs/SUBMISSION-LOG.md README.md
  git commit -m "docs(publication): arXiv submission confirmed [ID]"
  git push
  ```

- [ ] **Announce publication**
  - GitHub repo description
  - GitHub discussions / issues
  - Social media / research communities (optional)

---

## Timeline

| Event | Target | Actual | Status |
|-------|--------|--------|--------|
| **Metadata prepared** | 2026-04-25 | 2026-04-25 | ✅ |
| **PDF conversion** | 2026-04-26 | ⏳ | Pending |
| **arXiv upload** | 2026-04-26 | ⏳ | Pending |
| **arXiv confirmation** | 2026-04-27 | ⏳ | Pending |
| **Workshop notification** | ~2026-05-15 | ⏳ | TBD |

---

## References

- **Paper**: F3.1_paper_integrated.md (8 sections, 750 lines, 18 citations)
- **Validation**: PHASE-3-VALIDATION-REPORT.md (5-seed grid, gate assessment)
- **Gating**: PHASE-4-GATING-PROTOCOL.md (Tier 1 PASS, Tier 2 roadmap)
- **Upload guide**: UPLOAD-CHECKLIST.md (step-by-step instructions)
- **Release plan**: RELEASE-CHECKLIST.md (F3.1–F3.2 roadmap)

---

**Owner**: Jorge Pessoa  
**Status**: Metadata complete, awaiting PDF conversion + arXiv upload  
**Date prepared**: 2026-04-25

