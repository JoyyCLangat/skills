"""Classify shell commands that change a Power Platform environment or risk a leak.

Matching is best-effort on the raw command string: shells allow endless ways
to spell the same command, so this is a guard rail that catches the normal
spelling Claude uses, not a sandbox. Claude Code's permission system remains
the hard control.
"""

from __future__ import annotations

import re
from typing import List, Optional

# pac CLI subcommands that change an environment. Read-only or local-only ones
# (solution export/unpack/pack/check/list, auth list, org who, env fetch) are
# deliberately absent so everyday work runs without prompts.
_PAC_MUTATIONS = re.compile(
    r"(?ix)\bpac(?:\.exe)?\s+(?:"
    r"solution\s+(?:import|delete|upgrade|online-version|publish|add-solution-component)"
    r"|admin\s+(?:create|delete|reset|copy|restore|assign-\S+|set-\S+|update-\S+|add-\S+|remove-\S+)"
    r"|env\s+(?:update-settings)"
    r"|data\s+(?:import|delete|bulk-delete)"
    r"|plugin\s+push"
    r"|pcf\s+push"
    r"|package\s+deploy"
    r"|(?:pages|paportal)\s+upload"
    r"|connector\s+(?:create|update)"
    r"|application\s+install"
    r"|copilot\s+(?:publish|create|delete)"
    r")\b"
)

# PowerShell modules for Dataverse and Power Platform administration.
_POWERSHELL_MUTATIONS = re.compile(
    r"(?i)\b(?:Import-CrmSolution\w*|Remove-Crm\w+|Set-Crm\w+|New-Crm\w+|Publish-CrmAllCustomization"
    r"|Remove-AdminPowerApp\w*|Reset-PowerAppEnvironment|Copy-PowerAppEnvironment"
    r"|Restore-PowerAppEnvironment|Remove-PowerAppEnvironment|Set-AdminPowerApp\w*)\b"
)

_DATAVERSE_URL = re.compile(r"(?i)\b[\w.-]+\.crm\d*\.dynamics\.com\b|\b[\w.-]+\.api\.crm\d*\.dynamics\.com\b")
_HTTP_CLIENT = re.compile(r"(?i)\b(?:curl|wget|Invoke-RestMethod|Invoke-WebRequest|irm|iwr)\b|(?:^|[;&|]\s*)http\s")
_HTTP_WRITE = re.compile(
    r"(?i)(?:-X\s*|--request\s+|-Method\s+)['\"]?(?:POST|PATCH|PUT|DELETE|MERGE)\b"
    r"|\s(?:-d|--data(?:-raw|-binary|-urlencode)?|--json|-Body)\s"
)

# Environment names that read as production. Used only to sharpen the prompt.
_PRODUCTION_HINT = re.compile(r"(?i)(?<![a-z])(?:prod|production|prd|live)(?![a-z])")


def environment_change_reason(command: str) -> Optional[str]:
    """Return why ``command`` changes a Power Platform environment, or None."""
    match = _PAC_MUTATIONS.search(command) or _POWERSHELL_MUTATIONS.search(command)
    if match:
        action = " ".join(match.group(0).split())
    elif _DATAVERSE_URL.search(command) and _HTTP_CLIENT.search(command) and _HTTP_WRITE.search(command):
        action = "a write request to the Dataverse Web API"
    else:
        return None

    if _PRODUCTION_HINT.search(command):
        return (
            f"impax-crm guard: `{action}` changes a Power Platform environment, and this command "
            "looks like it targets PRODUCTION. Approve only if the change was agreed for Production "
            "and a backup or rollback plan exists."
        )
    return (
        f"impax-crm guard: `{action}` changes a Power Platform environment. Confirm the target "
        "is the environment you intend (normally Dev), not Production."
    )


_GIT = r"\bgit(?:\s+-C\s+\S+|\s+-c\s+\S+)*\s+"
GIT_COMMIT = re.compile(_GIT + r"commit\b")
GIT_COMMIT_ALL = re.compile(_GIT + r"commit\b[^|;&]*\s(?:-a\b|--all\b|-[A-Za-z]*a[A-Za-z]*\b)")
GIT_PUSH = re.compile(_GIT + r"push\b")
_NO_VERIFY = re.compile(r"\s--no-verify\b")
_FORCE_PUSH = re.compile(_GIT + r"push\b[^|;&]*\s(?:--force(?:-with-lease)?\b|-f\b)")
_PROTECTED_BRANCH = re.compile(r"(?<![\w/-])(?:main|master|release/\S+)\b")


def git_policy_reasons(command: str) -> List[str]:
    """Return reasons a git command needs the user's confirmation."""
    reasons: List[str] = []
    if (GIT_COMMIT.search(command) or GIT_PUSH.search(command)) and _NO_VERIFY.search(command):
        reasons.append("impax-crm guard: `--no-verify` skips the repository's safety hooks.")
    if _FORCE_PUSH.search(command) and _PROTECTED_BRANCH.search(command):
        reasons.append("impax-crm guard: force-pushing to a protected branch rewrites shared history.")
    return reasons
