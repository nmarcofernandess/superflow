---
name: review
description: "Review a Superflow spec before it becomes tasks, or reviewed code after GREEN, recording findings with verdicts and re-verification in review_log.json. Use when the user asks for review, critique, second opinion, or before QA closes a package that shipped code."
---

# Review

Review finds what the plan did not know. TDD proves the behavior you planned;
review proves nothing else broke, and that the spec was worth planning.

The reviewer is not the author. Use a second agent, a fresh pass, or a human —
never the same context that just wrote the code defending it.

## Required Reading

1. `../../assets/references/review-contract.md`
2. `../../assets/references/tdd-contract.md` (R4 proof follows the iron law)
3. `../../assets/references/status-schema.md`
4. `../../assets/templates/review_log.json`

## Procedure

1. Pick the kind: `spec` (R1, before Plan hardens) or `code` (R2, after GREEN
   and before QA).
2. Read the target: `SPEC.md` / `analysis.md` for spec review; the task diff,
   `implementation_plan.json` and `implementation_log.json` for code review.
   Review the **diff**, not the corrected file — reading the fixed version
   gives every defect a clean bill of health.
3. Set `phases.review = "running"` in `status.json`.
4. Write findings into `review_log.json`: `id`, `severity`
   (`blocker|major|minor|nit`), `claim`, `evidence` (`path:line` or the command
   that shows it). Findings start `pending`.
5. Answer every finding (R3): `accepted` (with `task_id` or `proof`),
   `rejected` (with the technical argument), or `deferred` (with owner or
   trigger). Agreement is not an argument.
6. Re-verify accepted blockers and majors (R4): fix, then record `proof` with
   `command`, `excerpt`, `ok`. Bugs get a failing test first.
7. Found nothing? Record the round with `findings: []` and a
   `no_findings_reason` that names what the diff touched.
8. Set `phases.review = "complete"` and `artifacts.review = "review_log.json"`.

## Severity

| Severity | Test |
|---|---|
| `blocker` | ships a defect, breaks a contract, or loses data |
| `major` | wrong behavior in a real path, or a test that proves nothing |
| `minor` | works, but the next reader pays for it |
| `nit` | preference; may be rejected without ceremony |

Do not inflate. A review of ten nits and no majors reads as a review that did
not look at the logic.

## Ready Gate

Review is not complete if:

- a finding is still `pending`;
- a `rejected` or `deferred` finding has no reason, or the reason is
  performative agreement instead of an argument;
- an `accepted` blocker or major has no `proof` with command and excerpt;
- a round has no findings and no `no_findings_reason`;
- the review read the corrected file instead of the diff;
- code shipped and no `kind: "code"` round exists.

Then run the package validator:

```bash
python3 <plugin-root>/scripts/validate_superflow.py <path-to-package>
```

Exit code must be 0.

## Mermaid

Not needed by default. If a finding is about flow or dependency, Mermaid only.
