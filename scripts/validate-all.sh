#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly PLUGIN="$ROOT/plugins/superflow"

python3 -I "$PLUGIN/scripts/validate_superflow.py" "$PLUGIN"

for test_name in test_model.py test_commands.py test_qg.py test_distribution.py; do
  test_path="$PLUGIN/scripts/$test_name"
  if [[ ! -f "$test_path" ]]; then
    echo "missing required test: $test_path" >&2
    exit 1
  fi
  python3 -I "$test_path"
done

echo "validate-all: passed"
