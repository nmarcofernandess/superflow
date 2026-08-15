---
name: campaign
description: "Drive a multi-package Superflow campaign to the end: compute what is actionable now, work that package through its phases, and refuse to declare done while any package is open. Use when several specs/NNN packages belong to one effort, when resuming a long campaign, or when the user asks what is next or whether a campaign is finished."
---

# Campaign

One package is a workflow. Several packages that only mean something together
are a campaign — a migration in slices, a foundation and its consumers, a spec
that grew into five.

The WARLOG narrates the campaign for a human. This skill drives it: it computes
what is actionable from the real packages, works that one, and comes back. It
does not let go of the bone.

## Required Reading

1. `../../assets/references/campaign-contract.md`
2. `../../assets/references/warlog-contract.md`
3. `../../assets/references/status-schema.md`

## Procedure

1. Ask the motor what is real:

```bash
python3 <plugin-root>/scripts/superflow_campaign.py <root> --campaign <name>
```

2. Read the verdict, not your memory of the session:

| Exit | Verdict | Do |
|---|---|---|
| 10 | `next` | work the named package |
| 20 | `blocked` | resolve a signed blocker — usually a human decision |
| 0 | `done` | the campaign is finished and the validator agrees |
| 1 | contract error | fix the graph or the package that lies about being closed |

3. Route the named package through `superflow` as usual: the phases it needs,
   TDD on code (`tdd-contract.md`), review before QA (`review-contract.md`).
4. Let the phase that did the work own its status update. This skill never
   writes another package's `status.json`.
5. Update `WARLOG.md` when the campaign's story moved: a sprint closed, a
   decision was made, a blocker appeared. Not per task.
6. Run the motor again. Repeat until it returns `done`.

## Joining a campaign

A package joins by carrying two fields in its own `status.json`:

```json
{"campaign": "export-v2", "depends_on": ["001-foundation"]}
```

`depends_on` holds package ids (directory names). There is no central campaign
file to keep in sync — and therefore none to drift.

## Blockers

A blocked package needs `blocked_reason` in its `status.json`, and the reason
names what would unblock it: a human decision, an upstream release, a missing
credential. "Blocked" with no reason fails the motor, because a blocker nobody
signed is an abandonment.

## Ready Gate

The campaign is not done if:

- the motor returns anything other than exit 0;
- a package claims `qa: complete` while
  `python3 <plugin-root>/scripts/validate_superflow.py <package>` refuses it;
- a blocked package has no `blocked_reason`;
- `depends_on` names a package that does not exist;
- the graph has a cycle;
- the report says done but you never re-ran the motor after the last package.

Do not close a campaign because the session got long. `done` is a computed
verdict, not a decision.

## Mermaid

The campaign map lives in `WARLOG.md` (`warlog-contract.md`), Mermaid only.
This skill does not draw a second graph.
