---
name: power-automate-flows
description: Design, build, review, and fix Power Automate cloud flows on Dataverse / Dynamics 365 — triggers and trigger conditions, error handling (try/catch scopes), loops and concurrency, pagination, child flows, connection references, run-only users, API limits, and avoiding infinite loops. Use when the user is building or reviewing a flow, a flow is failing or slow, or they ask whether to use a flow vs a plugin.
---

# Power Automate Flows (Dataverse)

## Design checklist

1. **Inside a solution**, using **connection references** and **environment variables** — not personal connections or hard-coded URLs/emails.
2. **Trigger narrowly.** Dataverse trigger *When a row is added, modified or deleted*:
   - **Select columns** — only the columns whose change matters (otherwise every save fires the flow).
   - **Filter rows** — OData filter, e.g. `statecode eq 0 and _ownerid_value ne null`.
   - **Trigger conditions** (Settings) for logic the filter can't express, e.g. `@not(equals(triggerOutputs()?['body/<prefix>_syncstatus'], 2))`.
   - **Scope**: Organization / Business unit / User as needed.
3. **Avoid loops.** A flow that updates the same row it triggers on must exclude its own update (select columns that the flow doesn't write, or a trigger condition on a flag/modified-by).
4. **Read efficiently.** *List rows*: use **Select columns** and **Filter rows**; set **Row count** or turn on **Pagination** with a threshold (default returns 5,000 max). Prefer FetchXML for joins/aggregates. Use *Get a row by ID* when you know the ID.
5. **Error handling.** Wrap the main logic in a **Scope "Try"**, then a **Scope "Catch"** with *Configure run after* = has failed / has timed out. In Catch: log (to a log table or Teams/email the support channel) including `workflow()?['run']?['name']` and a link to the run, then **Terminate** with status Failed so the run shows red.
6. **Loops.** Avoid *Apply to each* over large sets; when needed, set **Concurrency** deliberately (on if order doesn't matter and no shared variable is set inside). Never *Set variable* inside a concurrent loop. Use `Select`/`Filter array` expressions instead of loops where possible.
7. **Child flows** for reuse (*Run a Child Flow*, both flows in a solution); set the child's connections to *Use this connection* in run-only users.
8. **Naming.** Flow: `<Area> - <Trigger> - <What it does>`. Rename every action to say what it does (`Get primary contact`, not `Get a row by ID 3`) — expressions reference action names, so rename **before** writing expressions.
9. **Ownership.** Owned by a service account / application user or a team, not a person who might leave. Co-owners set.
10. **Limits.** Mind Power Platform request limits per licence and connector throttling (HTTP 429). Batch, filter early, and avoid polling.

## Flow vs. other options

- Must block or alter the save in the same transaction → **plugin** (`dynamics-plugin-development`).
- Simple show/hide/require/default on a form → **business rule**.
- Scheduled bulk processing of 100k+ rows → consider an Azure Function / Data Factory, or batch in pages.

## Diagnosing a failing flow

1. Open the failed run; find the first red action; read its **inputs and outputs**.
2. Common causes: connection expired / owner left; missing privilege for the connection's user; null value in an expression (use `coalesce()` / `?[]`); 429 throttling; 5,000-row pagination cut-off; lookup set with wrong syntax — Dataverse lookups need `<entitysetname>(<guid>)`, e.g. `accounts(00000000-0000-0000-0000-000000000000)`.
3. Fix in Dev inside the solution, then **resubmit** failed runs if the data still needs processing (check idempotency first).
4. Count how many runs failed in the period (blast radius) before telling the client it's fixed.

## Review output

When reviewing a flow (from export/definition JSON or screenshots), report: trigger efficiency, loop risk, error handling, hard-coded values, ownership, naming, and limits — each as OK / Issue + fix.
