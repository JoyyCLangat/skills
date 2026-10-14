# Impax CRM skills

Agent skills for CRM work at Impax Africa: Microsoft Dynamics 365, Dataverse, and the Power Platform, plus the delivery work around them (discovery, specs, UAT, releases, and client comms).

They're packaged as a Claude Code **plugin** (`impax-crm`). Install it once and Claude picks the right skill automatically in every session. You don't need to remember skill names.

## Install (once per computer)

In Claude Code, run:

```
/plugin install impax-crm --marketplace JoyyCLangat/skills
```

Or from a terminal:

```bash
claude plugin marketplace add JoyyCLangat/skills
claude plugin install impax-crm@impax-skills
```

To get updates, run `/plugin marketplace update impax-skills`.

### Claude Code on the web (cloud sessions)

- **Sessions on this repo** load the skills automatically through `.claude/skills`.
- **Sessions on other repos:** add this to that repo's `.claude/settings.json`:

  ```json
  {
    "extraKnownMarketplaces": {
      "impax-skills": { "source": { "source": "github", "repo": "JoyyCLangat/skills" } }
    },
    "enabledPlugins": { "impax-crm@impax-skills": true }
  }
  ```

## Skills

| Skill | Use it when |
|---|---|
| `impax-crm-context` | Starting any Impax or Dynamics task. It loads the Impax playbook, explains things in plain language, picks the right skill, and records new Impax conventions as they come up. |
| `crm-requirements-discovery` | You have a client brief, workshop notes, or an RFP, and need a requirements register with fit-gap against out-of-the-box Dynamics 365. |
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

## The Impax playbook (learns as you work)

`plugins/impax-crm/skills/impax-crm-context/references/impax-playbook.md` collects Impax conventions as they come up in sessions: tools, naming, process, and glossary. At the end of a task, Claude offers to add anything new, through a pull request you approve.

**This repo is public.** Never put client names, environment URLs, credentials, personal data, or pricing in it. Make the repo private if you want to keep client-specific knowledge here too.

## Repo layout

```
.claude-plugin/marketplace.json        # makes this repo installable as a marketplace
plugins/impax-crm/.claude-plugin/plugin.json
plugins/impax-crm/skills/<skill>/SKILL.md
.claude/skills -> plugins/impax-crm/skills   # loads the skills when you work in this repo
scripts/validate-skills.sh
```

## Adding or changing a skill

1. Create `plugins/impax-crm/skills/<name>/SKILL.md`. Its frontmatter needs a `name` that matches the folder, and a `description` that says what the skill does and when to use it.
2. Add the skill to the table above.
3. Run `./scripts/validate-skills.sh` and `claude plugin validate .`.
4. Bump `version` in `plugins/impax-crm/.claude-plugin/plugin.json`.

Some skills borrow workflow ideas from [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master). Each one names its source.
