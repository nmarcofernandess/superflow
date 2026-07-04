#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$ROOT/plugins/superflow/scripts/validate_superflow.py" "$ROOT/plugins/superflow"
python3 "$ROOT/plugins/superflow/scripts/test_superflow_routes.py"
python3 "$ROOT/plugins/superflow/scripts/forward_test_superflow.py"

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$ROOT"
  claude plugin validate "$ROOT/plugins/superflow"
fi

if command -v codex >/dev/null 2>&1; then
  codex plugin marketplace list >/dev/null
fi
