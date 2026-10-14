#!/usr/bin/env bash
# Checks every plugins/impax-crm/skills/<name>/SKILL.md has frontmatter with a matching name and a description.
set -euo pipefail
cd "$(dirname "$0")/.."
fail=0
for dir in plugins/impax-crm/skills/*/; do
  name=$(basename "$dir")
  file="$dir/SKILL.md"
  if [[ ! -f "$file" ]]; then echo "✗ $name: missing SKILL.md"; fail=1; continue; fi
  if [[ "$(head -1 "$file")" != "---" ]]; then echo "✗ $name: no frontmatter"; fail=1; continue; fi
  fm=$(awk 'NR==1{next} /^---$/{exit} {print}' "$file")
  fm_name=$(sed -n 's/^name: *//p' <<<"$fm")
  [[ "$fm_name" == "$name" ]] || { echo "✗ $name: frontmatter name '$fm_name' does not match folder"; fail=1; }
  grep -q '^description: .\+' <<<"$fm" || { echo "✗ $name: missing description"; fail=1; }
  grep -q "\`$name\`" README.md || { echo "✗ $name: not listed in README.md"; fail=1; }
done
[[ $fail -eq 0 ]] && echo "✓ all skills valid"
exit $fail
