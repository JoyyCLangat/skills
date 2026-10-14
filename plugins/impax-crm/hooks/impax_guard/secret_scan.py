"""Detect credentials and bulk personal data in text.

This module is the single source of truth for "what counts as a secret" in
this repository. The PreToolUse guard uses it to block writes and commits,
and scripts/validate.py uses it to scan the repository in CI.

Design notes:
- Detection favours precision over recall. A guard that cries wolf gets
  disabled, so each rule targets a concrete credential format or a literal
  value assigned to a secret-named key. It is a safety net, not a vault.
- Placeholders ({SECRET}, <secret>, ${VAR}, xxx, changeme, ...) never match.
- A line containing the marker ``impax-guard: allow`` is skipped, for the
  rare reviewed false positive.
- Findings never include the full secret, so reporting a finding can't leak it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Pattern, Tuple

ALLOW_MARKER = "impax-guard: allow"

# Text beyond this many characters is not scanned. Guard hooks run on every
# write, so an unbounded scan of a huge generated file would stall the session.
# One million characters covers any hand-written source or config file.
MAX_SCAN_CHARS = 1_000_000

# Lowercased substrings that mark a value as a placeholder rather than a secret.
_PLACEHOLDER_HINTS = (
    "{", "}", "<", ">", "$", "%", "xxx", "***", "...", "your", "example",
    "changeme", "change-me", "placeholder", "dummy", "redacted", "fake",
    "sample", "todo", "replace", "insert", "secret-name", "notreal",
)


@dataclass(frozen=True)
class Finding:
    rule: str
    line: int
    preview: str  # redacted: first 4 characters of the match, then an ellipsis

    def describe(self) -> str:
        return f"{self.rule} on line {self.line} ({self.preview})"


def _redact(value: str) -> str:
    value = value.strip().strip("'\"")
    return (value[:4] + "…") if len(value) > 4 else "…"


def _is_placeholder(value: str) -> bool:
    lowered = value.lower()
    if any(hint in lowered for hint in _PLACEHOLDER_HINTS):
        return True
    # A run of one repeated character ("aaaaaaaa", "00000000") is filler.
    stripped = lowered.strip("'\"")
    return len(set(stripped)) <= 2


# Each rule: (name, compiled pattern, index of the group holding the secret
# value or None to use the whole match, whether placeholder filtering applies).
_Rule = Tuple[str, Pattern[str], Optional[int], bool]

_RULES: List[_Rule] = [
    (
        "private key",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
        None,
        False,
    ),
    (
        # Microsoft Entra ID client secrets: 3 chars, a digit, "Q~", then 31-34 chars.
        "Entra ID client secret",
        re.compile(r"(?<![A-Za-z0-9_~.-])[A-Za-z0-9_~.-]{3}\dQ~[A-Za-z0-9_~.-]{31,34}(?![A-Za-z0-9_~.-])"),
        None,
        False,
    ),
    (
        "connection string credential",
        re.compile(
            r"(?i)\b(?:ClientSecret|Password|Pwd|AccountKey|SharedAccessKey|SharedAccessSignature)\s*=\s*([^;'\"\s]{6,})"
        ),
        1,
        True,
    ),
    (
        "hard-coded secret value",
        re.compile(
            # Lookarounds instead of \b so prefixed names (mpesa_passkey, dbPassword) match too,
            # while suffixed ones (password_hint, secretName) don't.
            r"(?i)[\"']?(?<![A-Za-z0-9])(?:[A-Za-z0-9]+[_-]?)?(?:client[_-]?secret|consumer[_-]?secret|consumer[_-]?key|pass[_-]?key|"
            r"api[_-]?key|access[_-]?token|auth[_-]?token|refresh[_-]?token|private[_-]?key|"
            r"password|passwd|secret)(?![A-Za-z0-9])[\"']?\s*[:=]\s*[\"']([^\"'\s]{8,})[\"']"
        ),
        1,
        True,
    ),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{60,}\b"), None, False),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"), None, False),
    ("OpenAI API key", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}"), None, False),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), None, False),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), None, False),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), None, False),
    ("Azure SAS signature", re.compile(r"[?&]sig=([A-Za-z0-9%/+]{30,})"), 1, True),
    (
        "bearer token (JWT)",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
        None,
        False,
    ),
]

# Secrets passed as command-line flags end up in shell history and transcripts.
# Only applied to shell commands. "-cs" is pac CLI's short form of --clientSecret;
# generic short flags such as "-p" are deliberately excluded (mkdir -p, ssh -p).
_CLI_SECRET_FLAG = re.compile(
    r"(?i)(?:^|\s)(?:--client-?secret|--password|--pwd|-cs)(?:\s+|=)(\"[^\"]+\"|'[^']+'|[^\s\"']+)"
)


def scan_text(text: str) -> List[Finding]:
    """Return credential findings in ``text``, one per line and rule."""
    findings: List[Finding] = []
    for line_no, line in enumerate(text[:MAX_SCAN_CHARS].splitlines(), start=1):
        if ALLOW_MARKER in line:
            continue
        for name, pattern, group, filter_placeholders in _RULES:
            for match in pattern.finditer(line):
                value = match.group(group) if group is not None else match.group(0)
                if filter_placeholders and _is_placeholder(value):
                    continue
                findings.append(Finding(name, line_no, _redact(value)))
                break  # one finding per rule per line is enough to report
    return findings


def scan_command_line(command: str) -> List[Finding]:
    """Scan a shell command, including secrets passed as CLI flags."""
    findings = scan_text(command)
    for line_no, line in enumerate(command.splitlines(), start=1):
        if ALLOW_MARKER in line:
            continue
        for match in _CLI_SECRET_FLAG.finditer(line):
            value = match.group(1)
            if _is_placeholder(value) or value.startswith("$"):
                continue
            findings.append(Finding("secret passed as a command-line flag", line_no, _redact(value)))
    return findings


# --- bulk personal data -----------------------------------------------------

# Kenyan mobile numbers: 07xx/01xx local or +254 7xx/1xx international.
_KE_PHONE = re.compile(r"(?<!\d)(?:\+?254|0)[17]\d{8}(?!\d)")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# One or two contact details in a file are normal (a support address, a sample).
# Dozens suggest an export of real customer data. These thresholds sit well
# above anything a skill, doc, or test fixture legitimately contains.
BULK_PHONE_THRESHOLD = 10
BULK_EMAIL_THRESHOLD = 25


def count_personal_data(lines: Iterable[str]) -> Tuple[int, int]:
    """Return (phone numbers, email addresses) found in ``lines``."""
    phones = emails = 0
    for line in lines:
        phones += len(_KE_PHONE.findall(line))
        emails += len(_EMAIL.findall(line))
    return phones, emails


def looks_like_bulk_personal_data(lines: Iterable[str]) -> bool:
    phones, emails = count_personal_data(lines)
    return phones >= BULK_PHONE_THRESHOLD or emails >= BULK_EMAIL_THRESHOLD
