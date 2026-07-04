# Superflow

Superflow is a portable Agent Skills workflow for routing raw requests into the
smallest honest phase set:

```text
request -> route -> inbox/PRD/build/plan -> execute -> QA
```

The reusable core is the `SKILL.md` tree under `plugins/superflow/skills`.
Codex and Claude Code are distribution surfaces, not separate sources of truth.
This repository is the marketplace root, like `code-flow`: product repositories
consume `superflow`, they do not host it.

## Repository Shape

```text
.agents/plugins/marketplace.json      # Codex marketplace catalog
.claude-plugin/marketplace.json       # Claude Code marketplace catalog
plugins/superflow/
  .codex-plugin/plugin.json           # Codex plugin manifest
  .claude-plugin/plugin.json          # Claude Code plugin manifest
  skills/                             # Portable Agent Skills core
  assets/                             # References, templates, and examples
  scripts/validate_superflow.py       # Structural validator
```

Do not copy this plugin into product repositories. Do not add
`plugins/superflow` or `.agents/plugins/marketplace.json` to consumer repos just
to use Superflow. Install this marketplace from Git and keep this repository as
the source.

## Install In Codex

```bash
codex plugin marketplace add nmarcofernandess/superflow --ref main
codex plugin add superflow@superflow
```

Refresh after updates:

```bash
codex plugin marketplace upgrade superflow
```

Start a new thread after installing or updating so the available skills list is
rebuilt.

## Install In Claude Code

Inside Claude Code:

```text
/plugin marketplace add nmarcofernandess/superflow
/plugin install superflow@superflow
/reload-plugins
```

Or from the shell when supported by your Claude Code version:

```bash
claude plugin marketplace add nmarcofernandess/superflow
claude plugin install superflow@superflow
```

Refresh after updates:

```text
/plugin marketplace update superflow
/plugin update superflow@superflow
/reload-plugins
```

## Design Rule

Agent Skills are the portable format. Plugin manifests and marketplaces are thin
runtime adapters. If workflow behavior changes, edit
`plugins/superflow/skills`, `plugins/superflow/assets`, or
`plugins/superflow/scripts` first and then bump the plugin manifests when
publishing a release.

## Validate

```bash
scripts/validate-all.sh
```

At minimum, the Superflow validators must pass:

```bash
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow
python3 plugins/superflow/scripts/test_superflow_routes.py
python3 plugins/superflow/scripts/forward_test_superflow.py
```
