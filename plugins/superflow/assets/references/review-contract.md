# Review Contract

Review is a phase, not a courtesy. It occupies the `critic` slot that existed
in `status.json` with no owner, no artifact, and no gate — now named `review`.

TDD proves the behavior you planned (`tdd-contract.md`). Review finds what the
plan did not know: the contract you broke elsewhere, the case the test does not
cover, the silent failure, the spec that decides two things at once. Green
tests and a passing review are different claims.

| Invariant | Owner |
|---|---|
| R1 — spec review before the plan hardens | `review` (target `SPEC.md` / `analysis.md`) |
| R2 — code review after GREEN, before QA | `review` (target task id or diff) |
| R3 — every finding gets a verdict with a reason | `review` |
| R4 — every accepted finding is re-verified | `review` + `execute` |

Artifact: `review_log.json` (`superflow.review.v1`). Template:
`assets/templates/review_log.json`.

## R1 — Spec review

Run against `SPEC.md` (or `analysis.md` when there is no spec), before Plan
turns it into tasks. The reviewer is not the author: a second agent, a second
pass with fresh context, or a human.

Look for: promise the backend cannot keep, facet that contradicts another,
architecture decision still open, acceptance criterion that no behavior can
prove, scope that is two slices wearing one hat.

A blocker here routes back to Build or Analyst. Do not "note it and plan
anyway".

## R2 — Code review

Run after GREEN, before QA closes. Target one plan task, one slice, or the
accumulated diff — whichever keeps the review small enough to be real.

Look for: behavior that passes its own test and breaks a caller, error
swallowed into a generic toast, contract changed on one side only, test that
asserts the implementation instead of the behavior, dead branch, copy that
ships instance prose.

Review does not replace RED/GREEN and does not re-litigate the architecture
that Build closed. If it wants to, that is an R1 finding filed late.

A round that found nothing must say why in `no_findings_reason` — what the diff
touched and why it carries no emergent risk. "Looks good" is not a reason, and
a silent empty round is a review that never happened.

## R3 — Receiving the review

Each finding carries a `verdict`:

| Verdict | Means | Requires |
|---|---|---|
| `pending` | not answered yet | nothing — but blocks QA |
| `accepted` | the finding is right | `task_id` or `proof` |
| `rejected` | the finding is wrong | `reason` with the technical argument |
| `deferred` | right, not now | `reason` naming the owner or the trigger |

**Agreement is not a verdict.** "Boa observação", "você tem razão", "good
catch", "makes sense" — these are noise where an argument belongs. A rejection
says what the reviewer got wrong about the code; an acceptance says what will
change. The validator refuses performative reasons by form.

Rejecting a finding is legitimate and expected. A review where every finding is
accepted is usually a review that was not read.

## R4 — Re-verification

An accepted finding is closed by evidence, not by an edit:

- **blocker / major** — `proof` with `command`, `excerpt`, `ok: true`. When the
  finding is a bug, the proof follows the iron law: a test that fails on the
  old behavior first.
- **minor / nit** — `task_id` is enough when the change is mechanical.

A boolean is not proof. "Should be fine now" is not proof.

## Package gate

When the package shipped code (`implementation_log.json` with completed tasks
that required TDD) and `phases.qa` is `complete`, the package needs a
`review_log.json` with at least one `kind: "code"` round and zero `pending`
findings.

There is no separate skip flag. To close without findings you declare the round
and sign the reason — `no_findings_reason` on the record beats a checkbox
nobody reads.

Docs-only packages (`workflow_type: docs` / `docs_only`) are exempt.

## Ownership

| Concern | Owner |
|---|---|
| Architecture and contracts | `build` |
| Task order and TDD pre-compile | `plan` |
| RED→GREEN iron law | `execute` |
| Findings, verdicts, re-verification | `review` |
| PRD acceptance matrix | `qa` |

Review reports; it does not silently rewrite the plan. An accepted finding
becomes a task, and the task follows the same TDD law as any other.
