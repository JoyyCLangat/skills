---
name: diagnosing-crm-issues
description: Hypothesis-driven diagnosis of Dynamics 365 / Dataverse / Power Platform problems — plugin errors, failing Power Automate flows, form script errors, "user can't see/edit record", slow forms or views, integration failures. Use when the user reports something broken, throwing, missing, or slow in CRM, or says "debug", "diagnose", "why is this happening".
---

# Diagnosing CRM Issues

Inspired by `troubleshooting` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master). Written for Dynamics 365 and the Power Platform.

Debugging is not guessing. No reproduction → no hypothesis.

## Phase 1 — Pin the symptom

Get, or look up yourself:

- **Exact error text** (and the downloaded log file from the error dialog), correlation ID, timestamp with timezone.
- **Who** — which user, their security roles, business unit, licence. Does it happen for a System Administrator?
- **Where** — environment (Dev/Test/UAT/Prod), app (model-driven app name), table, form, view.
- **What changed** — recent solution imports, Microsoft release wave updates, flow edits, new users or roles. Check the solution history (`Solutions > See history`).

Completion: you can state the symptom in one sentence that names user, environment, record/table, and action.

## Phase 2 — Reproduce

Reproduce it in the lowest environment that shows it, with the same role as the affected user (test user, or "impersonate" via a test account — never borrow credentials). Record exact steps.

If it only happens in Prod, say so and collect evidence there **read-only**.

Completion: a step list that makes the failure appear on demand, or an explicit statement of why it cannot be reproduced and what evidence you will use instead.

## Phase 3 — Gather evidence (pick the sources that fit)

| Symptom area | Where to look |
|---|---|
| Plugin / custom workflow activity | Plugin Trace Log (enable *Exception* or *All* in System Settings > Customization); Plugin Registration Tool profiler; step's stage/mode/filtering attributes; execution depth. |
| Power Automate flow | Run history → failed action inputs/outputs; trigger conditions; connection reference owner; concurrency; throttling (429). |
| Form / JavaScript | Browser DevTools console and network tab; `formContext` errors; event handler registration order; Monitor (`&monitor=true` / Power Apps Monitor). |
| "Can't see / can't edit" | Security role privileges and depth, record owner + BU, sharing (Access Checker / "Check access"), field security profiles, hierarchy security, form/view role assignment, app module role assignment. |
| Business rules / calculated / rollup | Scope (Entity vs. form), order vs. JavaScript on the same field, rollup job schedule. |
| Duplicate / missing data | Audit history on the record; duplicate detection rules; integration logs; bulk delete jobs; System Jobs (async operations) grid. |
| Slow | Form: too many tabs/subgrids/onload calls (use Monitor). View/query: FetchXML on unindexed `like '%x%'`, too many linked entities. Async backlog in System Jobs. |
| Integration | Service endpoint / webhook failures in System Jobs; Azure Service Bus dead-letter; API limit headers (`x-ms-ratelimit-*`); app user's security role. |

Completion: the evidence (log lines, run IDs, screenshots) is captured and cited, not paraphrased.

## Phase 4 — Hypothesise

List **3–5 ranked, falsifiable hypotheses**: "If X is the cause, then changing Y will make it go away." Show them to the user before testing — they often know "we imported a patch yesterday".

## Phase 5 — Blast radius (mandatory before fixing)

The reporter is rarely the only one affected. Write a FetchXML/OData/Dataverse query (see `dataverse-queries`) that finds **every record or user in the same state**. Report: "Reporter is 1 of N."

- N = 1 → fix only.
- N > 1 → fix + data repair plan (bulk update, flow, or script) the user approves.
- Any money, invoicing, or customer-facing communication affected → also draft a client notification with `client-comms`.

## Phase 6 — Fix and verify

- Fix the **root cause** in Dev, inside a solution — never a one-off manual change in Prod unless it's an approved emergency, in which case record it for back-porting.
- Re-run the Phase 2 reproduction: it must pass. Re-test with the affected user's role, not as admin.
- Turn plugin trace logging back to *Exception* (or *Off*) if you raised it.

## Phase 7 — Close out

State the confirmed root cause in one sentence for the ticket. Ask: what would have caught this earlier (a UAT script step, a flow failure alert, a role test)? Add it to the ticket as a follow-up if it isn't done now.
