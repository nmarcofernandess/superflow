# Backlog Status Protocol

Use this to verify whether existing GitHub issues are actually resolved,
without touching GitHub or code. This is reconciliation of claims already made
(in PR descriptions, commit messages, comments) against what is verifiably
true today — not classification of a new request (`audit`) and not discovery
of an unknown bug (`investigate_first`).

## Mission

For each issue in scope, produce a verdict backed by evidence: is the
described problem actually fixed in the target branch, partially fixed with a
named gap, blocked on a human decision, not touched at all, or genuinely
unclear. Every verdict traces to a `path:line`, a command + its output, or a
specific PR/commit — never to a title or a vibe.

## Non-Negotiables

- Read-only against GitHub and against code in v1. Do not close, comment on,
  or edit issues as a side effect of running this protocol — report the
  verdict and let the human or a separate explicit action act on it.
- An issue's GitHub state (`OPEN`/`CLOSED`) is evidence, not the verdict. Many
  repos merge fix PRs into a working branch (`dev`, `staging`) that is not the
  GitHub default branch — GitHub only auto-closes an issue when the "Closes
  #N" merge lands on the **default** branch. An issue sitting `OPEN` after its
  fix merged into a non-default branch is a tracker mechanic, not a stalled
  fix. Always check `gh repo view --json defaultBranchRef` and compare against
  where the fixing PR actually merged before treating "still open" as a
  finding.
- A PR title or its own "Closes #N" claim is not proof. Confirm the PR
  actually merged (`gh pr view <PR> --json state,mergedAt,baseRefName`), and
  when the claim is non-trivial or clinically/financially sensitive, read the
  real code the PR touched to confirm the described behavior is what's there
  today — PRs can under-deliver, get partially reverted, or be superseded by a
  later PR that changed the approach.
- Distinguish "resolved but deliberately left open" from "resolved and simply
  forgotten." Authors sometimes request manual/human closure on purpose (e.g.
  after a human validation step, or because a product decision needs
  ratification) — that is a different category from a fix nobody followed up
  on. Read the PR's own closing/merge comments for this signal before
  assuming neglect.
- Never report a confident verdict on insufficient evidence. `INCERTO`
  (uncertain) is a legitimate, expected outcome — say exactly what evidence is
  missing (e.g., "no PR references this issue number", "the migration this
  depends on has no confirmation it ran in prod").
- No silent scope cuts. If an issue bundles multiple sub-claims and only some
  are provably fixed, say which ones per claim — do not average into one
  verdict that hides an unresolved sub-claim.

## Procedure

### 1. Pull the issue

```bash
gh issue view <N> --json title,state,body,labels,comments,closedAt
```

Read the full body (the original claim/repro/acceptance criteria) and every
comment — later comments often carry diagnosis, scope changes, or open
questions posed back to the requester that never got an answer. A comment
asking "Option A or Option B?" with no reply is a live blocker, not
background noise.

### 2. Find the PR(s) that touched it

```bash
gh pr list --search "<N> in:body" --state all
git log --all --grep="#<N>" --oneline
```

An issue can have more than one PR: an initial fix plus a follow-up that
closed remaining gaps, or a follow-up that fixed a regression the first PR
introduced. Read all of them in chronological order — the last one is not
automatically the complete picture.

### 3. Confirm the merge is real, and where

```bash
gh pr view <PR> --json state,baseRefName,mergedAt
gh repo view --json defaultBranchRef
```

Merged and merged-into-the-branch-that-matters are different facts. If the
project's active development branch differs from the GitHub default branch,
expect every merged-but-not-into-default fix to show the issue as `OPEN` —
that is the single most common false "still pending" signal. Name it
explicitly in the report rather than let it read as neglect.

### 4. Spot-check the real code when the claim is non-trivial

Do not stop at the PR diff summary for anything where correctness matters
(data integrity, money, clinical/safety-relevant behavior, security). Open the
actual file(s) on the target branch and confirm the described behavior is
what's there — grep for the function/component named in the issue or PR body,
read the relevant lines, and check whether tests exist and cover the specific
scenario the issue described (not just "tests exist somewhere near this").

Also check for PR-declared manual follow-ups that don't show up in any diff:
a config change in a third-party dashboard, a one-time SQL/data-backfill
script that "needs to run once in each environment," an email template that
needs manual editing. These are exactly the kind of pendency that looks done
(code merged, tests green) but isn't operationally complete. If the PR itself
says "not run yet" or "Marco wasn't available to run this," treat that as
fact until you find evidence it changed — do not assume time passing means it
happened.

### 5. Classify

Use exactly one of these verdicts per issue (or per sub-claim, if the issue
bundles more than one):

| Verdict | Meaning |
|---|---|
| `RESOLVIDO (comprovado)` | Code + tests confirmed on target branch; nothing outstanding. Only reason it's still open is tracker mechanics or a deliberate manual-close request. |
| `RESOLVIDO (decisão revisada)` | The fix exists, but it satisfies a *different*, later product decision than the issue's original acceptance criteria — closing it is a product ratification, not a technical follow-up. Say what changed and who needs to confirm. |
| `PARCIALMENTE RESOLVIDO` | Core code fix confirmed, but a specific, named action remains (extra symptom with no PR, a manual script/config step not confirmed as run, an explicitly out-of-scope item from the fixing PR). List each remaining item concretely — never "some polish remains." |
| `BLOQUEADO EM DECISÃO HUMANA` | The technical/UI symptom may already be patched, but the issue's actual core complaint turns out to be a deliberate, documented product/contract decision, not a bug — it needs a human answer (often a literal unanswered question left in a comment), not more code. |
| `NÃO RESOLVIDO` | No credible PR/commit addresses it; the described behavior still reproduces as described. |
| `INCERTO` | Evidence is insufficient to call it either way. State exactly what you could not check and why (e.g., couldn't verify a prod-only manual step from a dev checkout). |

### 6. Report

For each issue: number, one-line title, GitHub state, related PR(s) with
their real merge target, verdict, and the evidence (path:line, or command +
literal output) that earned that verdict. When a verdict is
`PARCIALMENTE RESOLVIDO`, `BLOQUEADO EM DECISÃO HUMANA`, or `INCERTO`, always
name the exact next action (what to run, what to decide, who to ask) — a
verdict without a next action is half a report.

## Output Shape

- **1-3 issues, or a single pointed question** ("is #461 actually fixed?"):
  answer in prose, inline, with the evidence — no document needed.
- **A heterogeneous sweep (~5+ issues)** the user will review as a batch and
  act on multiple items at once (close some, ratify a decision on others,
  dispatch action items on the rest): render as an `html-didatico` mural,
  Direction A (manual de operação) — one card per issue with a color-coded
  verdict badge, the evidence, and the exact remaining action when there is
  one. Use `html-didatico`'s own skill for the document itself; this protocol
  only supplies the verified content that goes into it.

## Difference from `audit`

`audit` scores a **new, forward** request — route, phase budget, confidence,
readiness gaps — before any work has happened. `backlog-status` reconciles
**existing** issues against work that has **already** happened (merged PRs,
shipped code). They never overlap: if there's no PR/commit history to check
against yet, it isn't a `backlog-status` job.

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Treating "issue is OPEN" as "not done" without checking default-branch mechanics | Produces a false backlog of "pending" work that's actually already shipped |
| Trusting a PR's own "Closes #N" / title without confirming merge and reading the diff | PRs can under-deliver, get reverted, or be superseded |
| Calling an issue resolved because "tests are green" without checking the tests cover the specific scenario in the issue | Green suite can still miss the exact symptom reported |
| Missing a manual/operational follow-up (script, config, email template) buried in a PR description | Code-complete is not the same as operationally complete |
| Averaging multiple sub-claims into one verdict | Hides a real unresolved piece behind an optimistic summary |
| Answering with confidence when evidence is thin | `INCERTO` with a named gap beats a wrong `RESOLVIDO` |
