# TDD Contract

Superflow owns product routing. This contract owns how code work proves
behavior. It absorbs three external lessons without importing foreign plugins:

| Source | What Superflow keeps |
|---|---|
| Superpowers TDD | Iron law: no production code before a real RED |
| Superpowers writing-plans | Plan pre-compiles the failing test and commands |
| ECC tdd-workflow | RED validity criteria, evidence excerpts, runner honesty |

Skills that touch code tasks must read this file:

- `skills/plan/SKILL.md`
- `skills/execute/SKILL.md`
- `skills/qa/SKILL.md`
- `assets/references/execution-contract.md`

## The three invariants

### I1 — Plan pre-compiles proof

Every executable code task in `implementation_plan.json` declares:

```json
{
  "behavior": "one-sentence user/system guarantee",
  "tdd": {
    "required": true,
    "red": {
      "test_file": "path/to/test.ts",
      "test_name": "rejects empty email",
      "command": "npm test -- path/to/test.ts -t 'rejects empty email'",
      "expected_failure": "feature missing or assertion that proves the gap"
    },
    "green": {
      "command": "npm test -- path/to/test.ts -t 'rejects empty email'",
      "expected": "PASS"
    },
    "negatives": ["empty input", "unauthorized"]
  },
  "acceptance_criteria": ["PRD criterion text or id"]
}
```

Plan is incomplete when a required TDD task is missing `behavior`,
`tdd.red.command`, `tdd.red.expected_failure`, or `tdd.green.command`.

Forbidden plan placeholders:

- "write tests later"
- "add unit tests"
- "TBD" / "TODO" as verification
- verification that only says "manual" for production code paths

### I2 — Execute obeys the iron law

For each task with `tdd.required: true` (default for code work):

```text
1. Write or adjust the planned test first
2. Run RED — observe the failure for the expected reason
3. Only then write minimal production code
4. Run GREEN on the same target
5. Optional refactor while green
6. Record red + green evidence in implementation_log.json
```

Production code before observed RED makes the task invalid. Do not keep the
production edit as "reference". Fix by replaying RED→GREEN.

Valid RED (from ECC):

- **Runtime RED:** the new/changed test runs and fails for the intended missing
  behavior or bug.
- **Compile-time RED:** the new test references the missing path and the compile
  failure is the intended RED signal.

Invalid RED:

- test never executed
- failure only from unrelated syntax, missing deps, or broken setup
- test passes immediately (already existing behavior)

### I3 — QA closes product and proof

QA is done only when:

1. Every PRD acceptance criterion maps to a task or direct evidence.
2. Every completed `tdd.required` task has red + green evidence in
   `implementation_log.json` (or equivalent package log).
3. Repo-native checks proportional to risk were run (type/lint/test/proof).
4. A green command that does not cover the criterion is rejected.

## When TDD is required

| Situation | `tdd.required` |
|---|---|
| Feature, bug fix, refactor of behavior | `true` (default) |
| New production function/module/API | `true` |
| Docs-only, copy-only, pure markdown | `false` with `skip_reason` |
| Config/chore with no behavior change | `false` with `skip_reason` |
| Human-approved throwaway prototype | `false` with `skip_reason` naming the human gate |

`workflow_type` values that default to optional TDD for the whole plan when
every subtask is non-code:

- `docs`
- `docs_only`

If any subtask touches production code paths, that subtask still requires TDD
unless explicitly skipped with reason.

## Direct execution (no plan file)

Lean `prd_execute` without `implementation_plan.json` still follows I2 for
code: write failing test, observe RED, implement, observe GREEN, then QA (I3).
Record evidence in `implementation_log.json` with a synthetic task id
`direct-1` when useful.

## Evidence shape (`implementation_log.json`)

```json
{
  "schema_version": "superflow.log.v1",
  "source_plan": "implementation_plan.json",
  "tasks": [
    {
      "id": "subtask-1-1",
      "status": "DONE",
      "red": {
        "command": "npm test -- form.test.ts -t 'rejects empty email'",
        "excerpt": "FAIL: expected 'Email required', got undefined",
        "ok": true
      },
      "green": {
        "command": "npm test -- form.test.ts -t 'rejects empty email'",
        "excerpt": "PASS",
        "ok": true
      },
      "notes": ""
    }
  ]
}
```

Booleans without command/excerpt are not evidence. "Should pass" is not
evidence.

## Verification loop (QA / post-task)

Proportional, not monorepo theatre:

1. Targeted test for the behavior (always for code)
2. Typecheck when the stack has one and types moved
3. Lint when the project gate requires it for the touched paths
4. UI/browser proof only when the acceptance is visual/journey

Do not require a global 80% coverage number. Require the planned behavior to be
proven.

## Review vs TDD

- **TDD** proves the behavior before and during implementation.
- **QA** proves PRD acceptance after implementation.
- **Code review** (optional) finds emergent risk; it does not replace RED/GREEN.

Review may use the plan task and PRD criteria as context. Diff-only review
without acceptance mapping is incomplete for Superflow closure.

## Anti-patterns

- Plan with empty `verification.command` for code tasks
- Execute marks `DONE` without red/green evidence
- QA reports "tests pass" without mapping to PRD criteria
- Competing foreign `/plan` or `/tdd` skills overriding Superflow package
  artifacts — Superflow package files remain canonical

## Ownership

| Concern | Owner |
|---|---|
| Route, budget, PRD readiness | Superflow router / taskgen / PRD skill |
| Task order and TDD pre-compile | `plan` |
| RED→GREEN iron law | `execute` |
| Acceptance matrix + proportional checks | `qa` |
| Campaign / WARLOG | separate contract (not this file) |
