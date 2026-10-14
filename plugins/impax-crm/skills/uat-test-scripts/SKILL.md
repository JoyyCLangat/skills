---
name: uat-test-scripts
description: "Writes User Acceptance Testing scripts and a test tracker from CRM user stories, acceptance criteria, or a release scope, and triages UAT feedback into bugs, environment issues, training needs, and change requests. Use when preparing UAT, writing test cases, building a test plan for a Dynamics 365 release, or processing a batch of UAT feedback."
---

# UAT Test Scripts

Inspired by `qa-handoff` and `qa-failed-triage` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master).

## Mode A — Write scripts

1. **Collect scope**: tickets or user stories with acceptance criteria, the security roles involved, and the UAT environment. If the user hasn't provided them, don't stop. Draft the scripts from what they described, mark every guess as `[ASSUMPTION: …]`, and end with the short list of facts needed to finalise them. A marked draft gives the user something to react to. Never present a guess as a confirmed behaviour.
2. **One script per business scenario**, end-to-end in the user's language (e.g. "Capture a new lead from a walk-in customer and qualify it to an opportunity"), not per field.
3. **Each script:**

| Field | Content |
|---|---|
| ID / Title | UAT-SALES-003 — Qualify lead to opportunity |
| Role | The security role to test as — **never System Administrator** |
| Preconditions | Data that must exist, user setup |
| Steps | Numbered, one action each, naming the exact app/area/button |
| Expected result | Per step where something should be visible |
| Requirement / ticket | Traceability |
| Result | Pass / Fail / Blocked + comments + screenshot |

4. **Add negative and permission tests**: a role that must *not* see/edit the record; required-field validation; duplicate detection; what happens offline/on mobile if in scope.
5. **Cover cross-cutting**: notifications/emails sent, flows triggered, integration outputs, dashboards/reports updated, audit history.
Completion: every acceptance criterion maps to at least one step; every role in scope has at least one script.

Output as markdown tables and offer an Excel tracker (one sheet per module, plus a summary sheet).

## Mode B — Triage UAT feedback

For each item the client logs, classify **with evidence**:

- **Bug** — behaviour contradicts the agreed acceptance criteria. Reproduce it (`diagnosing-crm-issues`).
- **Environment/data issue** — missing role, stale data, solution not yet deployed to UAT, flow off. Fix the setup, not the code.
- **Training** — system works as designed; the user didn't know how.
- **Change request** — new or different behaviour than agreed. Route to `client-comms` (change request reply).
- **Duplicate.**

Report a summary: counts per class, blockers for sign-off, and the next action for each item.
