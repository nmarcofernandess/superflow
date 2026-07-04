# GitHub Issue Contract

GitHub issues are the right home for braindump, inbox, backlog, discussion, and
ideas that should not yet become local repo work.

## Labels

Use labels when available, but do not fail if the repo has no labels yet.

| Label | Meaning |
|-------|---------|
| `sf:inbox` | Captured idea, not committed to local execution |
| `sf:prd` | Issue body follows PRD layout |
| `sf:ready` | Can be promoted to local PRD |
| `sf:blocked` | Needs decision or missing external context |
| `sf:executing` | Has a linked local package or active work |

## Body Layout

Use the same PRD layout as `references/prd-contract.md`, with this header:

```md
<!-- superflow:issue v1 -->

Source: github_issue
Confidence: low|medium|high
Route: inbox_only|inbox_prd|local_prd|...
Phase budget: capture|lean|standard|deep|forensic
Local package: specs/NNN-slug or none
```

## Promotion

Promoting an issue means:

1. Read the current issue body.
2. Convert or preserve the PRD layout.
3. Create `specs/NNN-slug/`.
4. Write `PRD.md`, `status.json`, and `progress.md`.
5. Update the issue body with local package path if GitHub write access exists.

Script path:

```bash
python3 scripts/superflow_github.py fetch 79 --output issue-79.md
python3 scripts/superflow_taskgen.py --from-file issue-79.md --promote-issue 79
python3 scripts/superflow_github.py promote 79 --root "$PWD"
python3 scripts/superflow_github.py link 79 --local-package specs/001-slug
```

Use `create --dry-run` before real issue creation when repository/auth context is
uncertain.

## Link Policy

- Prefer relative repo paths in issue body when the doc lives in the same repo.
- Include absolute local paths only in local reports, not public GitHub issues.
- If an issue points to a local-only doc, say it is local-only and not clickable
  from GitHub for other users.

## Do Not

- Do not create issues for local-only tasks unless asked.
- Do not make every issue a local folder.
- Do not treat a low-confidence issue as execution-ready.
