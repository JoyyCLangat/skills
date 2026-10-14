---
name: impax-crm-context
description: Background and working style for Impax Africa CRM work — use at the start of ANY task involving Impax, its clients, Microsoft Dynamics 365, Dataverse, Power Apps, Power Automate, or CRM support/implementation. Sets beginner-friendly explanations, routes to the right impax-crm skill, and captures newly learned Impax conventions so later sessions know them.
---

# Impax CRM Context

The user is a **technology specialist in the CRM department at Impax Africa** (Impax Business Solutions — a Microsoft Dynamics partner headquartered in Nairobi, Kenya, with clients across East Africa). They are **new to the role**.

## 1. Load what's already known

Read `references/impax-playbook.md` (next to this file) before doing the task. It holds the conventions learned in earlier sessions. Prefer it over generic advice in the other skills when they conflict.

## 2. Work in beginner mode

- **Plain language first.** Define a term the first time it appears ("a *solution* — the package your changes travel in between environments").
- **Say which skill you're using and why** in one line, e.g. "Using `crm-impact-analysis` because deleting a column can break reports."
- **Show the why, briefly** — one sentence on the reason behind a rule, so the user learns it, not just follows it.
- **Safe by default.** Work in Dev/sandbox. Never change a Production environment, import a solution, delete data, or send anything to a client without the user's explicit go-ahead. Offer a draft or a checklist instead.
- **Point to a human when it's a judgment call.** Pricing, scope, contract, and anything legal → suggest checking with their lead.

## 3. Route to the right skill

| The user is… | Skill |
|---|---|
| Given a client brief, notes, RFP, or new request | `crm-requirements-discovery` |
| Turning agreed requirements into tasks/user stories | `functional-spec-to-tickets` |
| About to rename/delete/change something existing | `crm-impact-analysis` |
| Facing something broken, slow, or "can't see" | `diagnosing-crm-issues` (and `crm-security-model` for access) |
| Changing forms, fields, buttons, JavaScript | `model-driven-app-customization` |
| Building/fixing an automation | `power-automate-flows` |
| Writing C# plugins | `dynamics-plugin-development` |
| Needing data out of CRM (counts, lists, reports) | `dataverse-queries` |
| Moving changes between environments | `dataverse-solution-alm` |
| Importing/migrating data | `crm-data-migration` |
| Connecting CRM to other systems (ERP, M-Pesa, SMS) | `crm-integrations` |
| Preparing client testing | `uat-test-scripts` |
| Shipping a release | `crm-release-notes` |
| Writing to a client | `client-comms` |

## 4. Learn as you go — capture Impax conventions

Whenever the session reveals something **true of how Impax works** — a naming convention, the publisher prefix pattern, which ticketing tool the team uses, the environment naming, a document template, an internal process, a preferred tool, a recurring client type, a glossary term — note it.

At the end of the task (or when the user says "wrap up"), list the new facts and ask: *"Add these to the Impax playbook?"* On yes:

- If the `JoyyCLangat/skills` repo is available in the session, add them to `references/impax-playbook.md` under the right heading, with the date learned, on a branch, and open a pull request for the user to approve.
- Otherwise, print the exact lines to add so the user can paste them in later.

**Never record in the playbook** — the repo is public:
- Client names, client-specific configurations, or anything under NDA
- Tenant/environment URLs, credentials, keys, connection strings
- Customer or staff personal data
- Pricing, rates, or margins

Client-specific notes belong in the client's project documentation, not here. If the user wants client knowledge to be remembered too, suggest making the repo private first.
