# skills

Agent skills (Claude Code, Cursor, and other `SKILL.md`-compatible agents) for CRM work at Impax Africa: Microsoft Dynamics 365, Dataverse, and the Power Platform, plus the delivery workflow around them (discovery, specs, UAT, releases, client comms).

Each skill lives in `skills/<skill-name>/SKILL.md`. `.claude/skills` is a symlink to `skills/`, so Claude Code picks them up automatically when you work inside this repo.

## Skills

### Delivery workflow

| Skill | Use it when |
|---|---|
| `crm-requirements-discovery` | Turning a client brief, workshop notes, or RFP into a requirements register with fit-gap against out-of-the-box Dynamics 365. |
| `grilling` | Stress-testing a plan, design, or estimate through rounds of questions until nothing is assumed. |
| `functional-spec-to-tickets` | Turning agreed requirements into build-ready user stories with Dataverse design and acceptance criteria. |
| `crm-impact-analysis` | Before renaming, deleting, or changing a column, table, choice, role, plugin, or flow. |
| `uat-test-scripts` | Writing UAT scripts and trackers, and triaging UAT feedback. |
| `crm-release-notes` | Writing client "what's new" notes and an internal deployment note. |
| `client-comms` | Drafting client emails: status updates, UAT invites, go-live/downtime notices, incidents, change requests. |

### Dynamics 365 / Power Platform engineering

| Skill | Use it when |
|---|---|
| `dataverse-solution-alm` | Working with solutions, publishers, `pac` CLI, source control, environment variables, and Dev → Test → Prod deployments. |
| `dynamics-plugin-development` | Writing, registering, testing, or reviewing C# plugins and Custom APIs. |
| `power-automate-flows` | Building, reviewing, or fixing cloud flows on Dataverse. |
| `model-driven-app-customization` | Working on forms, views, business rules, BPFs, the command bar, JavaScript web resources, or PCF controls. |
| `dataverse-queries` | Writing FetchXML, Web API/OData, flow filters, or TDS SQL queries. |
| `crm-data-migration` | Planning or running migrations: mapping, cleansing, load order, upserts, and reconciliation. |
| `crm-security-model` | Designing or troubleshooting BUs, roles, teams, and field security, and covering data-protection requirements. |
| `crm-integrations` | Integrating with ERPs, M-Pesa (Daraja), SMS gateways, and portals through the Web API, Service Bus, Functions, or flows. |
| `diagnosing-crm-issues` | Debugging hypothesis-first: plugin errors, failing flows, permission problems, slow forms, broken integrations. |

### Working with agents

| Skill | Use it when |
|---|---|
| `session-handoff` | Parking work in a pickup note for the next session or a colleague. |
| `loose-ends` | Sweeping a session for unfinished follow-ups and temporary changes before you close it out. |
| `writing-great-skills` | Creating or editing skills in this repo. |

## Install

**In this repo:** open it in Claude Code. The skills load from `.claude/skills`.

**Everywhere (personal):**

```bash
git clone https://github.com/JoyyCLangat/skills.git ~/code/skills
mkdir -p ~/.claude/skills
for d in ~/code/skills/skills/*/; do ln -sfn "$d" ~/.claude/skills/"$(basename "$d")"; done
```

**Into one project:** copy (or symlink) the skill folders you want into that project's `.claude/skills/`.

## Adding a skill

Follow `skills/writing-great-skills/SKILL.md`, add the skill to the table above, then run:

```bash
./scripts/validate-skills.sh
```

Never put client names, tenant URLs, credentials, or customer data in a skill. Use `{PLACEHOLDERS}`.

## Credits

Several workflow skills are adapted from or inspired by [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master) and [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT). Each `SKILL.md` names its source. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
