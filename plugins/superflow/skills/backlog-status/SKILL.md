---
name: backlog-status
description: "Reconcile existing GitHub issues against merged PRs and real code to verify whether they are actually resolved. Use when the user asks whether a list of issues/bugs is already fixed, wants a status sweep of open backlog, asks to close stale issues, or wants to know why issues stay open after merge. Different from `audit`: audit scores ONE forward request before work starts; backlog-status verifies N existing issues against work already done."
---

# Backlog Status

Read-only reconciliation of GitHub issues against the real state of the
repository. Never closes, comments, or edits an issue by itself in v1 — it
reports a verdict per issue with evidence; the human or a follow-up action
decides what to do with it.

## Procedure

1. Read `../../assets/references/backlog-status-protocol.md` before starting —
   it has the full step-by-step, the verdict vocabulary, and the branch-default
   heuristic that explains most "why is this still open" confusion.
2. For each issue in scope, follow the protocol's verification chain: issue
   state/body/comments → related PR(s) → real merge target and merge state →
   spot-check the actual code when the claim is non-trivial → classify with
   one of the fixed verdicts.
3. Decide output shape per the protocol's guidance: prose for 1-3 issues or a
   single pointed question; an `html-didatico` mural (Direction A) for a
   heterogeneous sweep of ~5+ issues the user will review as a batch decision.
4. Do not invent resolution. If evidence is insufficient, the verdict is
   `INCERTO` (uncertain) with what's missing — never round up to a confident
   verdict to look complete.

## Commands

No dedicated script exists for this in v1 — the verification judgment (reading
PR bodies, matching claims to code) does not compress into a heuristic without
producing false precision. Use `gh`/`git` directly:

```bash
gh issue view <N> --json title,state,body,labels,comments,closedAt
gh pr list --search "<N> in:body"
gh pr view <PR> --json state,baseRefName,mergedAt
git log --all --grep="#<N>" --oneline
gh repo view --json defaultBranchRef
```

`scripts/superflow_github.py` (`fetch`/`promote`/`link`) is for issue-to-PRD
promotion, not for this — do not reach for it here.
