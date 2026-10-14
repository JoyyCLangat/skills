"""Inspect what a pending `git commit` or `git push` would publish."""

from __future__ import annotations

import fnmatch
import posixpath
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from .secret_scan import Finding, looks_like_bulk_personal_data, scan_text

# A diff over git's own pipe is fast; ten seconds only trips on a wedged
# repository (lock held, network filesystem), and then the guard steps aside
# rather than freezing the session.
GIT_TIMEOUT_SECONDS = 10

# Files that hold credentials by their nature. Matched against the basename.
SENSITIVE_FILE_PATTERNS = (
    ".env", ".env.*", "*.pfx", "*.p12", "*.key", "id_rsa", "id_rsa*", "id_ed25519*",
    "*.publishsettings", "local.settings.json", "secrets.json", "*.kdbx",
)
# Templates that look sensitive by name but are meant to be committed.
SAFE_TEMPLATE_SUFFIXES = (".example", ".sample", ".template", ".dist")

# Data files that commonly carry customer records (exports, migration loads, dumps).
DATA_FILE_PATTERNS = ("*.csv", "*.tsv", "*.xlsx", "*.xls", "*.bak", "*.bacpac", "*.mdf", "*.dump")


@dataclass
class PendingChange:
    """What a commit or push would publish."""

    added_lines_by_file: dict = field(default_factory=dict)  # path -> list of added lines
    files: List[str] = field(default_factory=list)


def _git(cwd: Optional[str], args: Sequence[str]) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def _parse_unified_diff(diff: str) -> PendingChange:
    change = PendingChange()
    current: Optional[str] = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[4:]
            current = None if path == "/dev/null" else path[2:] if path.startswith("b/") else path
            if current is not None:
                change.files.append(current)
                change.added_lines_by_file.setdefault(current, [])
        elif line.startswith("+") and not line.startswith("+++") and current is not None:
            change.added_lines_by_file[current].append(line[1:])
    return change


def pending_commit(cwd: Optional[str], include_unstaged: bool) -> Optional[PendingChange]:
    """Changes the commit would record, or None if git can't tell us."""
    staged = _git(cwd, ["diff", "--cached", "--no-color", "--no-ext-diff", "-U0"])
    if staged is None:
        return None
    diff = staged
    if include_unstaged:
        unstaged = _git(cwd, ["diff", "--no-color", "--no-ext-diff", "-U0"])
        diff += "\n" + (unstaged or "")
    change = _parse_unified_diff(diff)
    # Binary files have no "+++" header in -U0 output; list them by name too.
    names = _git(cwd, ["diff", "--cached", "--name-only"]) or ""
    for name in names.splitlines():
        if name and name not in change.files:
            change.files.append(name)
    return change


def pending_push(cwd: Optional[str]) -> Optional[PendingChange]:
    """Changes in local commits the upstream doesn't have yet, or None."""
    upstream = _git(cwd, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
    if upstream is None:
        return None  # new branch: its content was already checked at commit time
    diff = _git(cwd, ["diff", "--no-color", "--no-ext-diff", "-U0", "@{upstream}...HEAD"])
    return _parse_unified_diff(diff) if diff is not None else None


def _matches(name: str, patterns: Sequence[str]) -> bool:
    base = posixpath.basename(name.replace("\\", "/")).lower()
    return any(fnmatch.fnmatch(base, pattern) for pattern in patterns)


def sensitive_files(change: PendingChange) -> List[str]:
    return [
        f for f in change.files
        if _matches(f, SENSITIVE_FILE_PATTERNS) and not f.lower().endswith(SAFE_TEMPLATE_SUFFIXES)
    ]


def data_files(change: PendingChange) -> List[str]:
    return [f for f in change.files if _matches(f, DATA_FILE_PATTERNS)]


def secret_findings(change: PendingChange) -> List[str]:
    """Human-readable secret findings, e.g. 'config.json: GitHub token on added line 3 (ghp_…)'."""
    results: List[str] = []
    for path, lines in change.added_lines_by_file.items():
        found: List[Finding] = scan_text("\n".join(lines))
        results.extend(f"{path}: {f.rule} on added line {f.line} ({f.preview})" for f in found)
    return results


def personal_data_files(change: PendingChange) -> List[str]:
    return [path for path, lines in change.added_lines_by_file.items() if looks_like_bulk_personal_data(lines)]
