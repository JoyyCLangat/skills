---
name: crm-release-notes
description: "Writes release notes for a Dynamics 365 / Power Platform deployment: a client-facing what's-new note for end users and an internal deployment note with solutions, versions, steps, and rollback plan. Use when a batch of CRM work is ready to deploy or has been deployed, or the user asks for release notes, a changelog, or a deployment summary."
---

# CRM Release Notes

Inspired by `generating-release-notes` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master).

## Steps

1. **Collect what shipped from evidence**: tickets in the release, merged PRs / commits since the last release tag, solution names and **version numbers** (from `Solution.xml` or the environment), and any manual deployment steps. Completion: every item in the notes traces to a ticket or commit.
2. **Write two documents.**

### A. Client / end-user notes

```markdown
# <System name> update — <date>

## What's new
- **<Benefit in user words>** — what changed and where to find it. (Who: <roles>)

## Improvements
## Fixes
- Fixed: <what the user experienced before>.

## What you need to do
- e.g. refresh your browser; new required field on the Account form.

## Questions? <support contact>
```

No schema names, no ticket numbers unless the client tracks them, no internal jargon. Group by the user's area (Sales, Service, Collections, Admin).

### B. Internal deployment note

```markdown
# Deployment <release id> — <env> — <date, time EAT>

| Solution | Version | Managed | Order |
|---|---|---|---|

## Pre-deployment
- Backup / copy of target environment taken (yes/no, link)
- Environment variables & connection references values for target env
## Deployment steps (in order)
## Post-deployment
- Turn on flows; check flow owner/connection
- Manual config not in solutions (e.g. settings, Business Unit/team setup, reference data)
- Smoke test list
## Rollback plan
## Tickets included
```

3. **Flag risks**: managed solution upgrades that delete components ("Upgrade" vs "Update"/"Stage for upgrade"), data migrations, anything irreversible.
