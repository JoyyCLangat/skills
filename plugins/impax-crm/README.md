# Impax CRM skills

A Claude plugin for CRM work at Impax Africa: Microsoft Dynamics 365, Dataverse, and the Power Platform, plus the delivery work around them (discovery, specs, UAT, releases, and client comms).

Install it once. Claude then picks the right skill from what you ask, so you don't need to remember skill names. In Claude Code, a guard also stops secrets leaking and asks before anything changes a live environment.

## Install

### Everywhere: claude.ai, the desktop app, Cowork, and Claude Code (recommended)

1. Open [claude.ai → Customize → Plugins](https://claude.ai/customize/plugins) (or **Customize** in the Claude desktop app).
2. Choose **Add → Add marketplace** and enter `JoyyCLangat/skills`.
3. Add the **impax-crm** plugin, then turn on **Sync automatically** so you get updates.

The plugin is saved to your account. Its skills work in chat, Cowork, and Claude Code sessions signed in with the same account, including cloud sessions. Run `/reload-plugins` in a Claude Code session that was already open.

### Claude Code only, on one computer

```
/plugin install impax-crm --marketplace JoyyCLangat/skills
```

Update later with `claude plugin update impax-crm@impax-skills`.

### Requirements for the guard

The guard hook runs in Claude Code only (chat and Cowork don't run hooks). It needs **Python 3.8+** on your PATH (`python3`, `python`, or `py -3`). Without Python, Claude Code shows a one-time warning and the skills still work, but the guard is off.

## Skills

| Skill | Use it when |
|---|---|
| `impax-crm-context` | Starting any Impax or Dynamics task. Sets safe defaults, explains things plainly, picks the right skill, and records new Impax conventions. |
| `crm-requirements-discovery` | You have a client brief, workshop notes, or an RFP, and need a requirements register with fit-gap against out-of-the-box Dynamics 365. |
| `grilling` | You want a plan, design, or estimate stress-tested through rounds of questions. |
| `functional-spec-to-tickets` | You're turning agreed requirements into build-ready user stories with acceptance criteria. |
| `crm-impact-analysis` | You're about to rename, delete, or change a column, table, choice, role, plugin, or flow. |
| `uat-test-scripts` | You're writing UAT scripts and trackers, or triaging UAT feedback. |
| `crm-release-notes` | You need a client "what's new" note and an internal deployment note. |
| `client-comms` | You're drafting a client email: status update, UAT invite, go-live or downtime notice, incident, or change request. |
| `dataverse-solution-alm` | You're working with solutions, publishers, the `pac` CLI, environment variables, or Dev → Test → Prod deployments. |
| `dynamics-plugin-development` | You're writing, registering, testing, or reviewing C# plugins or Custom APIs. |
| `power-automate-flows` | You're building, reviewing, or fixing cloud flows on Dataverse. |
| `model-driven-app-customization` | You're changing forms, views, business rules, BPFs, the command bar, JavaScript, or PCF controls. |
| `dataverse-queries` | You need FetchXML, Web API/OData, flow filters, or TDS SQL. |
| `crm-data-migration` | You're planning or running a data migration: mapping, cleansing, load order, and reconciliation. |
| `crm-security-model` | You're designing or troubleshooting BUs, roles, teams, or field security, or checking data-protection requirements. |
| `crm-integrations` | You're connecting CRM to an ERP, M-Pesa (Daraja), an SMS gateway, or a portal. |
| `diagnosing-crm-issues` | Something is broken, slow, or "can't see", and you need to debug it hypothesis-first. |
| `session-handoff` | You're stopping work that someone (or a later session) will pick up. |
| `loose-ends` | You're closing out a session and want to catch follow-ups and temporary changes. |
| `writing-great-skills` | You're creating or editing a skill in this plugin. |

## Security

See [SECURITY.md](https://github.com/JoyyCLangat/skills/blob/main/SECURITY.md). In short:

- **Guard hook** (Claude Code). It **blocks** writing a secret into a file, passing one on the command line, and committing or pushing secrets or credential files. It **asks first** before `pac solution import`, deletes, resets, plugin pushes, Dataverse Web API writes, and similar commands, and gives a stronger warning when the target looks like Production. It also asks before committing data files or bulk personal data.
- **Skill rules** (every surface). Production is read-only without explicit approval. Client emails are drafts only. Email and record content is treated as data, never as instructions. Personal data is kept to a minimum, per the Kenya Data Protection Act 2019.
- **CI.** Every pull request runs the guard's tests, a secret scan of the whole repo, skill-spec validation, and strict plugin validation.

## The Impax playbook (learns as you work)

`plugins/impax-crm/skills/impax-crm-context/references/impax-playbook.md` collects Impax conventions as they come up in sessions: tools, naming, process, and glossary. At the end of a task, Claude offers to add anything new through a pull request you approve.

**This repo is public.** The playbook must never contain client names, URLs, credentials, personal data, or pricing. CI rejects URLs, emails, and phone numbers in it.

## Development

```bash
pip install -r requirements-dev.txt              # PyYAML, hash-pinned
python3 -m unittest discover -s tests            # guard tests
python3 scripts/validate.py                      # skills, manifests, hooks, secret scan
claude plugin validate --strict .                # Claude Code's own checks
claude plugin eval plugins/impax-crm --runs 1 --ablation none   # behaviour evals (uses model credits)
```

Releasing: bump `version` in `plugins/impax-crm/.claude-plugin/plugin.json` whenever plugin files change (CI enforces this). Without a bump, users don't receive the update. Use patch for wording fixes, minor for new or changed skills, and major for breaking changes.

To add a skill, follow `writing-great-skills`: write an eval first, keep frontmatter to the portable fields, add the skill to the table above, and run the checks.

### Layout

```
.claude-plugin/marketplace.json            # makes this repo a plugin marketplace
plugins/impax-crm/
  .claude-plugin/plugin.json               # plugin manifest (bump version on release)
  skills/<skill>/SKILL.md                  # the skills
  hooks/hooks.json, run-guard.sh, guard.py # the guard
  hooks/impax_guard/                       # secret scanner, command and git checks
  evals/<case>/                            # behaviour tests for claude plugin eval
.claude/skills -> plugins/impax-crm/skills # loads the skills when working in this repo
.claude/settings.json                      # runs the guard when working in this repo
scripts/validate.py, check_version_bump.py
tests/test_guard.py
.github/workflows/ci.yml, evals.yml
```

## Credits

Some skills borrow workflow ideas from [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master). Some adapt [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT). Each skill names its source. See [THIRD_PARTY_NOTICES.md](https://github.com/JoyyCLangat/skills/blob/main/THIRD_PARTY_NOTICES.md).
