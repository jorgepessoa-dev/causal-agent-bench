# Draft: upstream license-clarification issue

**Repo to file on**: `withmartian/routerbench`
**Command** (when authorized):

```bash
gh issue create --repo withmartian/routerbench \
    --title "Dataset license clarification (HF dataset card missing \`license\` field)" \
    --body-file docs/upstream_issue_draft.md
```

(the command above reads from *this* file — strip the top 3 lines
before filing, or paste the body manually into the web UI)

---

## Body

Hi — thanks for the great paper and corpus. I'm preparing a derived, annotated extension of RouterBench for a public benchmark (`causal-agent-bench`, Apache-2.0) and hit a license-verification block I'd love your help closing.

**What's clear:**
- Code repo (`withmartian/routerbench`) is MIT ✓
- Paper: arXiv:2403.12031 ✓ — will cite regardless of below

**What's ambiguous:**
- The HF dataset at `withmartian/routerbench` has **no `license` field** on the dataset card (verified via `GET https://huggingface.co/api/datasets/withmartian/routerbench` — siblings return `routerbench_0shot.pkl`, `routerbench_5shot.pkl`, `routerbench_raw.pkl`; metadata has no license). The dataset README also has no license tag.

**My two questions:**
1. Which license applies to the pickled data files?
2. Is it OK to redistribute an annotated subset (adding task-type / difficulty labels of our own, not re-hosting model outputs beyond what's already public in your pickles)?

A one-line `license:` entry on the HF dataset card would help the entire community, not just this benchmark. Happy to open a PR against the HF card if that's simpler on your end.

Thanks!
