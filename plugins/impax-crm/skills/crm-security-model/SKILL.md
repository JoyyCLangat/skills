---
name: crm-security-model
description: "Designs, reviews, and troubleshoots Dynamics 365 / Dataverse security: business units, security roles and privilege depth, owner, access, and Entra ID group teams, field-level and hierarchy security, sharing, app access, auditing, and data-protection duties such as the Kenya Data Protection Act. Use when designing roles, onboarding users, preparing an access review, or when a user cannot see or edit a record or sees too much."
---

# CRM Security Model

## Building blocks

| Concept | Use it for |
|---|---|
| **Business units (BU)** | Organisational data boundaries (branches, regions, subsidiaries). Keep the tree shallow. |
| **Security roles** | What a user can do per table, and at what **depth**: User → Business Unit → Parent:Child BUs → Organization. Plus Append / Append To / Assign / Share. |
| **Teams** | *Owner* teams (own records, carry roles), *Access* teams (per-record sharing templates), **Entra ID group teams** (membership managed in Entra ID — preferred for onboarding at scale). |
| **Field security profiles** | Hide/protect sensitive columns (ID numbers, salary, credit limit). |
| **Hierarchy security** | Managers see their reports' records (manager or position hierarchy). |
| **Sharing** | Exceptions only — heavy sharing hurts performance and is hard to audit. |
| **App / form / view access** | Which model-driven apps and forms a role sees. Not a security boundary on its own. |

Modern BUs let a user hold roles in BUs other than their own (matrix access) — consider before building complex sharing.

## Design steps

1. **List personas** (e.g. Relationship Manager, Branch Manager, Call Centre Agent, Collections Officer, Marketing, Admin, Integration app user) and what each must create/read/update/delete per table, and at what scope.
2. **Draft a role matrix** (rows = tables, columns = personas, cells = C/R/W/D/A/AT depth). Start from the least privilege that lets them work; **copy** a standard role rather than editing Microsoft's base roles.
3. **Map to BUs/teams.** Prefer roles assigned to Entra ID group teams so access follows the client's AD groups.
4. **Sensitive data** → field security profiles; decide who can read vs. update.
5. **Service accounts** → application users with a dedicated least-privilege role (not System Administrator).
6. **Auditing** on for sensitive tables/columns; agree retention.
7. **Test** each persona with a test user: positive (can do their job) and negative (can't see other branches' customers, can't export/delete if not allowed). Feed into `uat-test-scripts`.

## Troubleshooting "can't see / can't do"

Check in this order and report the first failure:

1. User enabled, licensed, in the right BU, has access to the app.
2. Role (direct or via team) has the privilege on that table **at a depth that covers the record's owner/BU**.
3. For lookups/relationships: **Append** on the child table and **Append To** on the parent.
4. Field security profile on the column.
5. Record owner / BU / sharing — use **Check access** on the record.
6. Form/view assigned to the user's roles.
7. Business rule/JS hiding it (not security, but looks like it).

## Data protection

For Kenya, the **Data Protection Act, 2019** (regulated by the ODPC) — and equivalents in Uganda, Tanzania, Rwanda, Nigeria, etc. Design for: lawful basis/consent capture, purpose limitation (who can see what and why), retention and deletion (bulk delete jobs / retention policies), data subject access requests (can you find and export everything about one person?), and audit trails. Flag requirements for the client's DPO to confirm — don't give legal advice.

## Output

Role matrix table, BU/team diagram (text), list of field security profiles, test users per persona, open questions.
