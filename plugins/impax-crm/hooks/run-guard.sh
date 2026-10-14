#!/usr/bin/env bash
# Launch guard.py with the first Python 3.8+ interpreter found.
# Stdin (the hook event) passes straight through to the guard via exec.
# Without Python the guard can't run: warn once per machine, then step aside
# so a missing interpreter never blocks normal work.
set -u

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
guard="$here/guard.py"

for candidate in python3 python "py -3"; do
  # shellcheck disable=SC2086  # "py -3" must split into command + flag
  if $candidate -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
    # -I: isolated mode, ignore PYTHON* env vars and the user site-packages.
    # shellcheck disable=SC2086
    exec $candidate -I "$guard"
  fi
done

marker="${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}}/impax-guard-no-python"
if [ ! -e "$marker" ]; then
  mkdir -p "$(dirname "$marker")" 2>/dev/null && : > "$marker" 2>/dev/null
  echo "impax-crm guard: Python 3.8+ not found, so secret and environment checks are OFF. Install Python 3 to enable them." >&2
  exit 1
fi
exit 0
