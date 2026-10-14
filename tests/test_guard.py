"""Tests for the impax-crm PreToolUse guard.

Fake credentials are assembled at runtime so this file never contains a
literal that secret scanners (ours, GitHub's) would flag.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "plugins" / "impax-crm" / "hooks"
sys.path.insert(0, str(HOOKS))

import guard  # noqa: E402
from impax_guard import commands, secret_scan  # noqa: E402

FAKE_ENTRA_SECRET = "abc" + "8Q~" + "K" * 10 + "x1Y2z3W4v5U6t7S8r9Q0p1O"  # 3 + 3 + 33 chars
FAKE_GITHUB_TOKEN = "gh" + "p_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
FAKE_LOGIN_VALUE = "Tr0ub4dor" + "&3horse"
PRIVATE_KEY_HEADER = "-----BEGIN " + "RSA PRIVATE KEY-----"


def run_guard(event: dict) -> dict:
    """Run guard.py as Claude Code does and return its parsed output ({} if none)."""
    proc = subprocess.run(
        [sys.executable, "-I", str(HOOKS / "guard.py")],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def decision(output: dict) -> str:
    return output.get("hookSpecificOutput", {}).get("permissionDecision", "none")


class SecretScanTests(unittest.TestCase):
    def assertFlags(self, text: str, rule: str) -> None:
        findings = secret_scan.scan_text(text)
        self.assertTrue(any(f.rule == rule for f in findings), f"expected {rule!r} in {findings}")

    def assertClean(self, text: str) -> None:
        self.assertEqual(secret_scan.scan_text(text), [], text)

    def test_detects_credential_formats(self):
        self.assertFlags(f'"clientSecret": "{FAKE_ENTRA_SECRET}"', "Entra ID client secret")
        self.assertFlags(f"token = {FAKE_GITHUB_TOKEN}", "GitHub token")
        self.assertFlags(PRIVATE_KEY_HEADER, "private key")
        self.assertFlags(
            f"AuthType=ClientSecret;Url=https://org.crm4.dynamics.com;ClientId=1;ClientSecret={FAKE_LOGIN_VALUE}",
            "connection string credential",
        )
        self.assertFlags(f'mpesa_passkey = "{FAKE_LOGIN_VALUE}"', "hard-coded secret value")
        self.assertFlags(f'"Password": "{FAKE_LOGIN_VALUE}"', "hard-coded secret value")
        self.assertFlags(f'dbPassword = "{FAKE_LOGIN_VALUE}"', "hard-coded secret value")
        self.assertFlags(f'user-password: "{FAKE_LOGIN_VALUE}"', "hard-coded secret value")

    def test_ignores_placeholders_and_references(self):
        self.assertClean('"clientSecret": "{CLIENT_SECRET}"')
        self.assertClean('"clientSecret": "<your-client-secret>"')
        self.assertClean("ClientSecret=${CLIENT_SECRET}")
        self.assertClean('password: "changeme-later"')
        self.assertClean('"password": "********"')
        self.assertClean("secret = os.environ['CLIENT_SECRET']")
        self.assertClean("Store the client secret in Azure Key Vault.")
        self.assertClean('password_hint = "Your first pet"')
        self.assertClean('"secretName": "kv-client-secret"')

    def test_allow_marker_skips_line(self):
        self.assertClean(f'"Password": "{FAKE_LOGIN_VALUE}"  # impax-guard: allow')

    def test_findings_never_contain_the_secret(self):
        for finding in secret_scan.scan_text(f'"clientSecret": "{FAKE_ENTRA_SECRET}"'):
            self.assertNotIn(FAKE_ENTRA_SECRET, finding.describe())

    def test_command_line_flags(self):
        found = secret_scan.scan_command_line(f"pac auth create --clientSecret {FAKE_LOGIN_VALUE}")
        self.assertTrue(any("command-line flag" in f.rule for f in found))
        self.assertEqual(secret_scan.scan_command_line('pac auth create --clientSecret "$CLIENT_SECRET"'), [])
        self.assertEqual(secret_scan.scan_command_line("mkdir -p build/output && ssh -p 22 host"), [])

    def test_bulk_personal_data_threshold(self):
        few = ["Call +254712345678 or 0712345679"]
        many = [f"+2547{n:08d}" for n in range(secret_scan.BULK_PHONE_THRESHOLD)]
        self.assertFalse(secret_scan.looks_like_bulk_personal_data(few))
        self.assertTrue(secret_scan.looks_like_bulk_personal_data(many))


class CommandClassificationTests(unittest.TestCase):
    def test_environment_changes_are_detected(self):
        for cmd in (
            "pac solution import --path out/Core_managed.zip --async",
            "pac solution delete --solution-name Core",
            "pac admin reset --environment 1234",
            "pac plugin push --pluginId 1",
            "pac data import --data data.zip",
            "Import-CrmSolution -SolutionFilePath core.zip",
            "curl -X PATCH https://org.crm4.dynamics.com/api/data/v9.2/accounts(1) -d '{}'",
            "Invoke-RestMethod -Method Delete -Uri https://org.api.crm4.dynamics.com/api/data/v9.2/contacts(1)",
        ):
            with self.subTest(cmd=cmd):
                self.assertIsNotNone(commands.environment_change_reason(cmd))

    def test_read_only_and_local_commands_pass(self):
        for cmd in (
            "pac solution export --name Core --path out/Core.zip",
            "pac solution unpack --zipfile out/Core.zip --folder src/Core",
            "pac solution pack --zipfile out/Core.zip --folder src/Core",
            "pac solution check --path out/Core_managed.zip",
            "pac solution sync",
            "pac auth list",
            "curl https://org.crm4.dynamics.com/api/data/v9.2/accounts?$top=5",
            "dotnet build && dotnet test",
        ):
            with self.subTest(cmd=cmd):
                self.assertIsNone(commands.environment_change_reason(cmd))

    def test_production_is_called_out(self):
        reason = commands.environment_change_reason("pac solution import --environment https://contoso-prod.crm4.dynamics.com")
        self.assertIn("PRODUCTION", reason)
        reason = commands.environment_change_reason("pac solution import --environment https://contoso-dev.crm4.dynamics.com")
        self.assertNotIn("PRODUCTION", reason)

    def test_git_policies(self):
        self.assertTrue(commands.git_policy_reasons("git commit --no-verify -m wip"))
        self.assertTrue(commands.git_policy_reasons("git push --force origin main"))
        self.assertEqual(commands.git_policy_reasons("git push --force origin feature/x"), [])
        self.assertEqual(commands.git_policy_reasons("git commit -m 'normal'"), [])


class GuardProcessTests(unittest.TestCase):
    """Black-box tests through stdin/stdout, exactly as Claude Code calls the hook."""

    def test_harmless_command_produces_no_output(self):
        self.assertEqual(run_guard({"tool_name": "Bash", "tool_input": {"command": "ls -la"}}), {})

    def test_environment_change_asks(self):
        out = run_guard({"tool_name": "Bash", "tool_input": {"command": "pac solution import --path a.zip"}})
        self.assertEqual(decision(out), "ask")

    def test_powershell_tool_is_covered(self):
        out = run_guard({"tool_name": "PowerShell", "tool_input": {"command": "Import-CrmSolution -SolutionFilePath a.zip"}})
        self.assertEqual(decision(out), "ask")

    def test_secret_on_command_line_is_denied(self):
        out = run_guard({"tool_name": "Bash", "tool_input": {"command": f"pac auth create -cs {FAKE_LOGIN_VALUE}"}})
        self.assertEqual(decision(out), "deny")
        self.assertNotIn(FAKE_LOGIN_VALUE, json.dumps(out))

    def test_deny_beats_ask(self):
        out = run_guard({"tool_name": "Bash", "tool_input": {
            "command": f"pac auth create -cs {FAKE_LOGIN_VALUE} && pac solution import --path a.zip"}})
        self.assertEqual(decision(out), "deny")

    def test_write_with_secret_is_denied(self):
        out = run_guard({"tool_name": "Write", "tool_input": {
            "file_path": "/repo/appsettings.json", "content": f'{{"ClientSecret": "{FAKE_ENTRA_SECRET}"}}'}})
        self.assertEqual(decision(out), "deny")

    def test_edit_with_placeholder_passes(self):
        out = run_guard({"tool_name": "Edit", "tool_input": {
            "file_path": "/repo/appsettings.json", "old_string": "a", "new_string": '"ClientSecret": "{CLIENT_SECRET}"'}})
        self.assertEqual(out, {})

    def test_unknown_tool_and_malformed_input_are_ignored(self):
        self.assertEqual(run_guard({"tool_name": "Read", "tool_input": {"file_path": "/x"}}), {})
        self.assertEqual(run_guard({"tool_name": "Bash", "tool_input": "not-a-dict"}), {})

    def test_invalid_json_fails_open(self):
        proc = subprocess.run([sys.executable, "-I", str(HOOKS / "guard.py")], input="{not json",
                              capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(proc.returncode, 1)  # non-blocking error, never a silent block
        self.assertEqual(proc.stdout, "")
        self.assertIn("internal error", proc.stderr)


@unittest.skipUnless(shutil.which("git"), "git not installed")
class GitCommitTests(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        self.git = lambda *a: subprocess.run(["git", *a], cwd=self.repo, check=True, capture_output=True, env=env)
        self.git("init", "-q")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def commit_event(self, command: str = "git commit -m test") -> dict:
        return {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": self.repo}

    def stage(self, name: str, content: str) -> None:
        Path(self.repo, name).write_text(content, encoding="utf-8")
        self.git("add", name)

    def test_clean_commit_passes(self):
        self.stage("README.md", "# Notes\nClient secret lives in Key Vault.\n")
        self.assertEqual(run_guard(self.commit_event()), {})

    def test_staged_secret_is_denied(self):
        self.stage("config.json", f'{{"token": "{FAKE_GITHUB_TOKEN}"}}\n')
        out = run_guard(self.commit_event())
        self.assertEqual(decision(out), "deny")
        self.assertIn("config.json", out["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertNotIn(FAKE_GITHUB_TOKEN, json.dumps(out))

    def test_credential_file_is_denied_but_template_passes(self):
        self.stage(".env", "API_URL=https://example.org\n")
        self.assertEqual(decision(run_guard(self.commit_event())), "deny")
        self.git("rm", "-q", "--cached", ".env")
        self.stage(".env.example", "API_URL=\n")
        self.assertEqual(run_guard(self.commit_event()), {})

    def test_commit_all_includes_unstaged_changes(self):
        self.stage("notes.md", "start\n")
        self.git("-c", "user.name=t", "-c", "user.email=t@example.org", "commit", "-q", "-m", "init")
        Path(self.repo, "notes.md").write_text(f'start\n"password": "{FAKE_LOGIN_VALUE}"\n', encoding="utf-8")
        self.assertEqual(run_guard(self.commit_event("git commit -m x")), {})  # not staged
        self.assertEqual(decision(run_guard(self.commit_event("git commit -am x"))), "deny")

    def test_data_files_ask(self):
        self.stage("contacts.csv", "name,phone\nA,+254712345678\n")
        self.assertEqual(decision(run_guard(self.commit_event())), "ask")


class HookManifestTests(unittest.TestCase):
    def test_hooks_json_points_at_existing_launcher(self):
        config = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        entry = config["hooks"]["PreToolUse"][0]
        for tool in ("Bash", "PowerShell", "Write", "Edit", "NotebookEdit"):
            self.assertIn(tool, entry["matcher"].split("|"))
        command = entry["hooks"][0]["command"]
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/run-guard.sh", command)
        self.assertTrue((HOOKS / "run-guard.sh").is_file())

    @unittest.skipUnless(shutil.which("bash"), "bash not installed")
    def test_launcher_passes_stdin_through(self):
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "pac solution delete --solution-name X"}})
        proc = subprocess.run(["bash", str(HOOKS / "run-guard.sh")], input=event, capture_output=True,
                              text=True, timeout=60, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(decision(json.loads(proc.stdout)), "ask")


if __name__ == "__main__":
    unittest.main()
