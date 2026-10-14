---
name: crm-impact-analysis
description: Map the blast radius of a Dynamics 365 / Dataverse change BEFORE making it — deleting or changing a column, table, choice/option set, relationship, security role, business process flow, plugin step, flow, or form. Use when the user plans to rename, delete, retype, or change behaviour of anything other components may depend on.
---

# CRM Impact Analysis

Inspired by `impact-analysis` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master), re-written for Dataverse.

Stop. Before touching a shared component, list everything that depends on it.

## Phase 1 — Name the change

One line: component, type of change (add / rename display name / change type / delete / change behaviour), environment, and solution it lives in.

Note: in Dataverse a column's **schema/logical name cannot be renamed** and its **data type mostly cannot change** — those become "create new + migrate + retire old". Say so up front if it applies.

## Phase 2 — Find consumers

Check each source and record what you found (including "none"):

1. **Show Dependencies** on the component in the maker portal (classic: Solution > component > Show Dependencies). Catches forms, views, charts, business rules, relationships, BPFs.
2. **Solution layers** — is the component in more than one solution or owned by a managed solution / ISV? Unmanaged change on top of a managed layer?
3. **Code** — search the repo(s) for the logical name: plugins (C#), JavaScript web resources, PCF controls, integration code, Azure Functions, Logic Apps, SSIS/KingswaySoft packages.
   `grep -rni "<logical_name>" .`
4. **Power Automate** — cloud flows in the solution and *outside* solutions (`Default Solution`), including flows owned by other users.
5. **Reports & analytics** — Power BI datasets, SSRS reports, Excel templates, Word templates, saved Advanced Find views (personal views are not in solutions!).
6. **Integrations** — anything reading/writing via Web API or TDS endpoint; ask the integration owner if unsure.
7. **Security** — field security profiles, column-level permissions, roles that reference the table.
8. **Data** — how many records have a value in the column / use the option? (count via FetchXML aggregate)
9. **Portals / Power Pages** — table permissions, basic/advanced forms, Liquid templates.

Completion: every source above has a finding with evidence.

## Phase 3 — Risk table

| Consumer | What it expects today | Breaks if… | Risk (H/M/L) | Mitigation |
|---|---|---|---|---|

High = data loss, integration failure, security exposure, or Prod-only consumer you can't test.

## Phase 4 — Plan the change

- Prefer **additive** changes: add the new thing, migrate consumers, then retire the old one in a later release.
- Deleting a column deletes its data permanently — back up first (export or copy column) and get explicit sign-off.
- Removing an option value: re-map existing records first.
- List the deployment order (e.g. solution A before solution B; data migration step between imports).
- List the UAT checks that prove nothing broke — feed them into `uat-test-scripts`.

Output the analysis as a short report the user can paste into the ticket.
