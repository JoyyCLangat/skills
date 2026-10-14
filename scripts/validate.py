#!/usr/bin/env python3
"""Validate the impax-crm plugin and this repository.

Checks, in order:
  1. Manifests: marketplace.json and plugin.json parse, agree on the plugin
     name, and carry a semantic version.
  2. Skills: every skills/<name>/SKILL.md follows the Agent Skills spec that
     claude.ai uploads enforce (portable frontmatter only, name and
     description rules) plus this repo's rules (third-person descriptions,
     under 500 lines, local links resolve, references one level deep).
  3. Coverage: every skill is listed in README.md and has at least one eval.
  4. Hooks: hooks.json parses and every referenced script exists.
  5. Hygiene: no tracked file contains a credential, and the public playbook
     contains no URLs, emails, or phone numbers.

Usage: python3 scripts/validate.py
Exit code 0 when clean, 1 on any error. Inside GitHub Actions, errors are
also emitted as annotations on the offending file and line.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a code path
    sys.exit("validate.py needs PyYAML: pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "impax-crm"
SKILLS = PLUGIN / "skills"
EVALS = PLUGIN / "evals"
PLAYBOOK = SKILLS / "impax-crm-context" / "references" / "impax-playbook.md"

sys.path.insert(0, str(PLUGIN / "hooks"))
from impax_guard.secret_scan import count_personal_data, scan_text  # noqa: E402

# Agent Skills spec: the only frontmatter keys claude.ai uploads and the Skills API accept.
PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024
RESERVED_WORDS = ("anthropic", "claude")
# Anthropic's guidance: keep SKILL.md under 500 lines; reference files over 100 lines need a contents list.
SKILL_MAX_LINES = 500
REFERENCE_TOC_THRESHOLD = 100
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
# Descriptions are injected into the system prompt; first/second person confuses discovery.
NON_THIRD_PERSON = re.compile(r"^(?:I|I'm|We|You|Use this|This skill)\b")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

# Large binaries and lockfiles aren't hand-written and only slow the scan down.
SCAN_SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".zip", ".pdf", ".lock"}


class Report:
    def __init__(self) -> None:
        self.errors = 0
        self.in_ci = os.environ.get("GITHUB_ACTIONS") == "true"

    def error(self, path: Path, message: str, line: Optional[int] = None) -> None:
        self.errors += 1
        rel = path.relative_to(ROOT) if path.is_absolute() else path
        where = f"{rel}:{line}" if line else str(rel)
        print(f"✗ {where}: {message}")
        if self.in_ci:
            loc = f"file={rel}" + (f",line={line}" if line else "")
            print(f"::error {loc}::{message}")


def load_json(path: Path, report: Report) -> Optional[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report.error(path, "missing")
        return None
    except json.JSONDecodeError as exc:
        report.error(path, f"invalid JSON: {exc}", exc.lineno)
        return None
    if not isinstance(data, dict):
        report.error(path, "top level must be an object")
        return None
    return data


def check_manifests(report: Report) -> None:
    market = load_json(ROOT / ".claude-plugin" / "marketplace.json", report)
    plugin = load_json(PLUGIN / ".claude-plugin" / "plugin.json", report)
    if not market or not plugin:
        return
    entries = {e.get("name"): e for e in market.get("plugins", []) if isinstance(e, dict)}
    name = plugin.get("name")
    if name not in entries:
        report.error(ROOT / ".claude-plugin" / "marketplace.json", f"no entry for plugin {name!r}")
    elif entries[name].get("source") != "./plugins/impax-crm":
        report.error(ROOT / ".claude-plugin" / "marketplace.json", "impax-crm source must be ./plugins/impax-crm")
    if not SEMVER_RE.match(str(plugin.get("version", ""))):
        report.error(PLUGIN / ".claude-plugin" / "plugin.json", "version must be semantic (MAJOR.MINOR.PATCH)")


def split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:]


def check_links(path: Path, body: str, report: Report, offset: int) -> List[Path]:
    """Verify relative links resolve; return the local markdown files linked."""
    linked: List[Path] = []
    for line_no, line in enumerate(body.splitlines(), start=offset):
        for target in MD_LINK.findall(line):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                report.error(path, f"broken link: {target}", line_no)
            elif resolved.suffix == ".md" and resolved.is_relative_to(path.parent):
                linked.append(resolved)
    return linked


def check_skill(skill_dir: Path, report: Report) -> None:
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        report.error(skill_dir, "missing SKILL.md")
        return
    text = path.read_text(encoding="utf-8")
    raw, body = split_frontmatter(text)
    if raw is None:
        report.error(path, "must start with YAML frontmatter between --- lines", 1)
        return
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        report.error(path, f"frontmatter is not valid YAML: {exc}", mark.line + 2 if mark else 1)
        return
    if not isinstance(meta, dict):
        report.error(path, "frontmatter must be a mapping", 1)
        return

    extra = sorted(set(meta) - PORTABLE_KEYS)
    if extra:
        report.error(path, f"non-portable frontmatter keys {extra}; claude.ai uploads reject them", 1)

    name = meta.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > NAME_MAX:
        report.error(path, f"name must be lowercase-hyphenated and at most {NAME_MAX} characters", 2)
    elif name != skill_dir.name:
        report.error(path, f"name {name!r} must match folder {skill_dir.name!r}", 2)
    elif any(word in name for word in RESERVED_WORDS):
        report.error(path, f"name must not contain {RESERVED_WORDS}", 2)

    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        report.error(path, "description is required", 3)
    else:
        if len(desc) > DESCRIPTION_MAX:
            report.error(path, f"description is {len(desc)} characters; limit is {DESCRIPTION_MAX}", 3)
        if "<" in desc or ">" in desc:
            report.error(path, "description must not contain angle brackets (XML tags are rejected)", 3)
        if NON_THIRD_PERSON.match(desc):
            report.error(path, "description must be third person ('Drafts…', not 'I…' / 'You…' / 'Use this…')", 3)
        if "Use when" not in desc:
            report.error(path, "description should say when to use the skill ('Use when…')", 3)

    total_lines = text.count("\n") + 1
    if total_lines > SKILL_MAX_LINES:
        report.error(path, f"{total_lines} lines; keep SKILL.md under {SKILL_MAX_LINES} and move detail to references/")

    body_offset = raw.count("\n") + 3
    for ref in check_links(path, body, report, body_offset):
        ref_text = ref.read_text(encoding="utf-8")
        nested = [t for t in MD_LINK.findall(ref_text) if t.endswith(".md") and not re.match(r"^[a-z]+:", t)]
        if nested:
            report.error(ref, "reference files must not link to further .md files (keep references one level deep)")
        if ref_text.count("\n") > REFERENCE_TOC_THRESHOLD and "## Contents" not in ref_text:
            report.error(ref, f"over {REFERENCE_TOC_THRESHOLD} lines; add a '## Contents' list at the top")


def eval_targets() -> Dict[str, int]:
    """Count eval cases per skill, from the skill named in each tool_used grader."""
    counts: Dict[str, int] = {}
    for grader in EVALS.glob("*/graders/*.md"):
        match = re.search(r"\(\?:\[\\w-\]\+:\)\?([a-z0-9-]+)", grader.read_text(encoding="utf-8"))
        if match:
            counts[match.group(1)] = counts.get(match.group(1), 0) + 1
    return counts


def check_coverage(skill_names: List[str], report: Report) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"^\| `([a-z0-9-]+)` \|", readme, re.M))
    for name in skill_names:
        if name not in listed:
            report.error(ROOT / "README.md", f"skill {name!r} missing from the skills table")
    for name in sorted(listed - set(skill_names)):
        report.error(ROOT / "README.md", f"skills table lists {name!r}, which doesn't exist")

    counts = eval_targets()
    for name in skill_names:
        if not counts.get(name):
            report.error(SKILLS / name / "SKILL.md", "no eval case triggers this skill (add one under plugins/impax-crm/evals/)")


def check_hooks(report: Report) -> None:
    path = PLUGIN / "hooks" / "hooks.json"
    config = load_json(path, report)
    if not config:
        return
    for event, groups in (config.get("hooks") or {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                for script in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", hook.get("command", "")):
                    if not (PLUGIN / script).is_file():
                        report.error(path, f"{event} hook references missing file {script}")


def tracked_files() -> List[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, check=True, timeout=30).stdout
        return [ROOT / p for p in out.decode("utf-8").split("\0") if p]
    except (OSError, subprocess.SubprocessError):
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


def check_hygiene(report: Report) -> None:
    for path in tracked_files():
        if path.suffix.lower() in SCAN_SKIP_SUFFIXES or not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for finding in scan_text(text):
            report.error(path, f"possible secret: {finding.rule} ({finding.preview})", finding.line)

    if PLAYBOOK.is_file():
        for line_no, line in enumerate(PLAYBOOK.read_text(encoding="utf-8").splitlines(), start=1):
            phones, emails = count_personal_data([line])
            if re.search(r"https?://|\.dynamics\.com", line) or phones or emails:
                report.error(PLAYBOOK, "public playbook must not contain URLs, emails, or phone numbers", line_no)


def main() -> int:
    report = Report()
    check_manifests(report)
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    for skill_dir in skill_dirs:
        check_skill(skill_dir, report)
    check_coverage([p.name for p in skill_dirs], report)
    check_hooks(report)
    check_hygiene(report)

    if report.errors:
        print(f"\n{report.errors} problem(s) found.")
        return 1
    print(f"✓ {len(skill_dirs)} skills, manifests, hooks, and repository hygiene all valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
