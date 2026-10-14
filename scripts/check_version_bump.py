#!/usr/bin/env python3
"""Fail when plugins/impax-crm changed but its version did not increase.

Claude Code only ships an update to users when plugin.json's version changes:
with the same version, `claude plugin update` reports "already at the latest
version" and users keep the old copy. Changes to the eval suite alone don't
reach users' behaviour, so they don't require a bump.

Usage: python3 scripts/check_version_bump.py <base-ref>   (e.g. origin/main)
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import List, Optional, Tuple

PLUGIN_DIR = "plugins/impax-crm/"
MANIFEST = PLUGIN_DIR + ".claude-plugin/plugin.json"
EXEMPT_PREFIXES = (PLUGIN_DIR + "evals/",)


def git(*args: str) -> Optional[str]:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False, timeout=30)
    return result.stdout if result.returncode == 0 else None


def parse_version(text: str) -> Tuple[int, int, int]:
    version = json.loads(text)["version"]
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"not a semantic version: {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    base = argv[1]
    merge_base = (git("merge-base", base, "HEAD") or "").strip()
    if not merge_base:
        print(f"✗ cannot find a merge base with {base}; fetch it first (git fetch origin)")
        return 1

    changed = (git("diff", "--name-only", merge_base, "HEAD") or "").splitlines()
    relevant = [p for p in changed if p.startswith(PLUGIN_DIR) and not p.startswith(EXEMPT_PREFIXES)]
    if not relevant:
        print("✓ plugin unchanged; no version bump needed")
        return 0

    old_manifest = git("show", f"{merge_base}:{MANIFEST}")
    if old_manifest is None:
        print("✓ plugin is new on this branch; no previous version to compare")
        return 0
    with open(MANIFEST, encoding="utf-8") as fh:
        new_version = parse_version(fh.read())
    old_version = parse_version(old_manifest)

    if new_version <= old_version:
        shown = "\n".join(f"  - {p}" for p in relevant[:10])
        print(
            f"✗ plugin files changed but version is {'.'.join(map(str, new_version))} "
            f"(base: {'.'.join(map(str, old_version))}). Bump 'version' in {MANIFEST}:\n"
            "  patch for wording fixes, minor for new or changed skills, major for breaking changes.\n"
            f"Changed:\n{shown}"
        )
        return 1
    print(f"✓ version {'.'.join(map(str, old_version))} → {'.'.join(map(str, new_version))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
