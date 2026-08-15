# Campaign Contract

A campaign is several packages that only mean something together: a migration
split into slices, a foundation plus its consumers, a spec that grew into five.

The WARLOG already tells that story to a human — mission, sprint cards,
dependencies, next action. What it cannot do is answer the two questions a
long campaign actually turns on:

1. What is genuinely actionable **right now**?
2. Is this campaign **finished**, or does it just look finished?

This contract owns those two answers. It does not fork the WARLOG.

| Artifact | Answers |
|---|---|
| `WARLOG.md` | the narrative: why these sprints, in this order, with this budget |
| `status.json` per package | where that package is, and what it waits on |
| `superflow_campaign.py` | the computed verdict over the real packages |

## C1 — The campaign is derived, not declared

There is no central campaign file. A package joins a campaign by carrying
`campaign` in its `status.json`, and states its order by carrying `depends_on`:

```json
{
  "campaign": "export-v2",
  "depends_on": ["001-foundation"],
  "phases": {"...": "..."}
}
```

The motor walks the package directories, reads those two fields, and computes
the graph. Nothing is duplicated, so nothing can drift: a package that moves is
already telling the truth about itself.

`depends_on` holds package ids (directory names). An id that does not exist is
a contract error, not a warning — a dependency you cannot name is a dependency
you have not thought about.

## C2 — Order comes from dependencies

A package is **actionable** when it is open and every dependency is closed.
Everything else waits.

A cycle is a contract error. Two packages that each wait for the other describe
work that cannot start, and the motor says so by name instead of looping.

## C3 — Closed is a verdict of the validator, not a checkbox

A package counts as closed when both hold:

- `phases.qa` is `complete`;
- `validate_superflow.py <package>` exits 0.

So closing a package still means: PRD acceptance mapped, RED/GREEN evidence for
every task that required TDD, and no review finding left `pending`
(`review-contract.md`). A package that claims `qa: complete` while the
validator refuses it fails the campaign — a lie about one slice is not a
rounding error in a campaign, it is the campaign.

## C4 — Do not let go of the bone

The motor reports one of four verdicts:

| Verdict | Exit | Means |
|---|---|---|
| `next` | 10 | at least one package is actionable — keep working |
| `blocked` | 20 | nothing actionable, and the campaign is not finished |
| `done` | 0 | every package in scope is closed |
| contract error | 1 | cycle, unknown dependency, or a package lying about being closed |

`done` is only ever reported when every package in scope is closed. There is no
partial victory, no "the important ones are done", no closing the campaign
because the session got long.

`blocked` is legitimate and must be **signed**: a package whose phase is
`blocked` needs `blocked_reason` in its `status.json`. Blocked without a reason
is not a blocker, it is an abandonment — and it fails the motor.

## Loop

```bash
python3 <plugin-root>/scripts/superflow_campaign.py <root> --campaign <name>
# exit 10 → work the package it named, then run it again
# exit 20 → resolve a signed blocker (usually a human decision)
# exit 0  → the campaign is finished, and the validator agrees
```

Each pass re-reads the real packages. Progress that exists only in the
conversation does not move the verdict.

## Not in scope

- The motor does not execute phases. It names the next package; `superflow`
  routes it and the phase skills do the work.
- The motor does not write `status.json`. The phase that did the work owns its
  own status, as everywhere else in Superflow.
- The motor does not rank by priority or value. Dependencies decide order;
  humans decide the rest in the WARLOG.
