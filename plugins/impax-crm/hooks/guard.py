#!/usr/bin/env python3
"""PreToolUse guard for the impax-crm plugin.

Reads the hook event from stdin and answers with a permission decision:

- deny: writing a secret into a file, passing one on the command line, or
  committing/pushing secrets or credential files.
- ask:  commands that change a Power Platform environment, committing data
  files or bulk personal data, and git commands that skip safety hooks or
  force-push a protected branch.
- no output: everything else, so normal work is never slowed down.

The guard fails open: if it crashes it reports the error on stderr (exit 1,
a non-blocking error in Claude Code) instead of blocking every tool call.
Requires Python 3.8+ and only the standard library.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from impax_guard import commands, git_checks  # noqa: E402
from impax_guard.secret_scan import scan_command_line, scan_text  # noqa: E402

# Hook payloads are small JSON objects; a payload this large is malformed.
MAX_STDIN_BYTES = 8 * 1024 * 1024

SECRET_ADVICE = (
    "Store secrets in Azure Key Vault, an environment variable of type Secret, or a pipeline "
    "secret variable, and refer to them by name (for example {CLIENT_SECRET}). If this is a "
    "reviewed false positive, add the comment `impax-guard: allow` on that line."
)

Decision = Tuple[str, str]  # (permissionDecision, reason)


def _bullets(items: List[str], limit: int = 5) -> str:
    shown = items[:limit]
    more = f"\n- …and {len(items) - limit} more" if len(items) > limit else ""
    return "\n".join(f"- {item}" for item in shown) + more


def check_shell(command: str, cwd: Optional[str]) -> List[Decision]:
    decisions: List[Decision] = []

    leaked = scan_command_line(command)
    if leaked:
        decisions.append((
            "deny",
            "impax-crm guard: this command contains a credential, which would be saved in shell "
            "history and the session transcript:\n" + _bullets([f.describe() for f in leaked]) +
            "\nRead the secret from an environment variable instead (for example `$env:CLIENT_SECRET` "
            "or `\"$CLIENT_SECRET\"`), or use certificate or interactive authentication.",
        ))

    env_reason = commands.environment_change_reason(command)
    if env_reason:
        decisions.append(("ask", env_reason))

    decisions.extend(("ask", reason) for reason in commands.git_policy_reasons(command))

    if commands.GIT_COMMIT.search(command):
        change = git_checks.pending_commit(cwd, include_unstaged=bool(commands.GIT_COMMIT_ALL.search(command)))
        decisions.extend(_review_change(change, "commit"))
    elif commands.GIT_PUSH.search(command):
        decisions.extend(_review_change(git_checks.pending_push(cwd), "push"))

    return decisions


def _review_change(change: Optional[git_checks.PendingChange], verb: str) -> List[Decision]:
    if change is None:
        return []
    decisions: List[Decision] = []

    secrets = git_checks.secret_findings(change)
    if secrets:
        decisions.append((
            "deny",
            f"impax-crm guard: this {verb} would publish what look like secrets:\n{_bullets(secrets)}\n"
            f"Remove them from the change (and rotate any real credential). {SECRET_ADVICE}",
        ))

    credential_files = git_checks.sensitive_files(change)
    if credential_files:
        decisions.append((
            "deny",
            f"impax-crm guard: this {verb} includes credential files:\n{_bullets(credential_files)}\n"
            "Unstage them (`git restore --staged <file>`) and add them to .gitignore. Commit a "
            "`.example` template with placeholder values instead.",
        ))

    data = git_checks.data_files(change)
    personal = git_checks.personal_data_files(change)
    if data or personal:
        decisions.append((
            "ask",
            f"impax-crm guard: this {verb} includes data that may hold customer personal data "
            f"(Kenya Data Protection Act 2019):\n{_bullets(sorted(set(data + personal)))}\n"
            "Commit only synthetic or masked data. Approve if you've confirmed it has no real "
            "customer records.",
        ))
    return decisions


def check_file_write(tool_input: Dict[str, Any]) -> List[Decision]:
    pieces: List[str] = []
    for key in ("content", "new_string", "new_source"):
        value = tool_input.get(key)
        if isinstance(value, str):
            pieces.append(value)
    for edit in tool_input.get("edits") or []:  # multi-edit payloads
        if isinstance(edit, dict) and isinstance(edit.get("new_string"), str):
            pieces.append(edit["new_string"])

    findings = scan_text("\n".join(pieces))
    if not findings:
        return []
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or "the file"
    return [(
        "deny",
        f"impax-crm guard: writing {target} would store what looks like a secret:\n"
        f"{_bullets([f.describe() for f in findings])}\n{SECRET_ADVICE}",
    )]


def decide(event: Dict[str, Any]) -> Optional[Decision]:
    tool = event.get("tool_name") or ""
    tool_input = event.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return None

    if tool in ("Bash", "PowerShell"):
        command = tool_input.get("command")
        decisions = check_shell(command, event.get("cwd")) if isinstance(command, str) else []
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        decisions = check_file_write(tool_input)
    else:
        return None

    if not decisions:
        return None
    # Claude Code ranks deny above ask; mirror that and merge the reasons.
    verdict = "deny" if any(d == "deny" for d, _ in decisions) else "ask"
    reasons = [r for d, r in decisions if d == verdict]
    return verdict, "\n\n".join(reasons)


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
        if len(raw) > MAX_STDIN_BYTES:
            print("impax-crm guard: hook input too large; skipped.", file=sys.stderr)
            return 1
        event = json.loads(raw.decode("utf-8"))
        result = decide(event) if isinstance(event, dict) else None
    except Exception as exc:  # fail open, visibly
        print(f"impax-crm guard: internal error ({type(exc).__name__}: {exc}); check skipped.", file=sys.stderr)
        return 1

    if result is not None:
        verdict, reason = result
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": verdict,
                "permissionDecisionReason": reason,
            }
        }, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
