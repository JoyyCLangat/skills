---
name: crm-data-migration
description: Plan and run data migration into Dynamics 365 / Dataverse from legacy CRMs, Excel, ERPs, or core systems — source analysis, field mapping, cleansing and de-duplication, load order, alternate keys and upserts, owners and dates, tool choice (Import wizard, Configuration Migration Tool, Dataflows, KingswaySoft/SSIS, Azure Data Factory), and reconciliation. Use when the user is migrating, importing, or bulk-loading data, writing a mapping document, or reconciling counts after a load.
---

# CRM Data Migration

## Steps

1. **Inventory sources.** For each: system, tables/sheets, record counts, owner, extract method, how clean it is. Ask what "active" means (e.g. customers transacting in the last 24 months) — migrating less is the biggest win.
2. **Mapping document** — one row per target column:

| Target table | Target column (logical) | Type | Source | Transform | Default | Required | Notes |
|---|---|---|---|---|---|---|---|

   Include choice mappings (source value → option value), lookup resolution (by alternate key or legacy ID column), and owner mapping (legacy user → Dataverse user/team).
3. **Cleanse and de-duplicate** before loading: phone numbers to one format (e.g. E.164 `+2547XXXXXXXX`), emails lower-cased and validated, names trimmed, national ID / KRA PIN formats, merge duplicates on an agreed rule. Report counts of what was fixed and rejected.
4. **Keys.** Add a `<prefix>_legacyid` column + **alternate key** on each migrated table so loads are re-runnable **upserts** and lookups resolve without GUIDs.
5. **Load order** (parents before children):
   1. Business units, users, teams (and their roles)
   2. Currencies, reference/config data (Configuration Migration Tool)
   3. Accounts → Contacts → (re-link primary contact on accounts)
   4. Leads / Opportunities / Cases / custom transactional tables
   5. Activities (emails, phone calls, tasks) and notes/attachments last — they are the biggest.
6. **Preserve history** where needed: `overriddencreatedon` for original created date; set `statecode`/`statuscode` in a second pass for closed records (closed opportunities/cases need their close messages, not a plain update).
7. **Business logic during load.** Decide per table whether plugins/flows should fire. Prefer the `BypassBusinessLogicExecution` / `BypassCustomPluginExecution` request options (requires privilege) over manually turning things off; if you must turn flows off, list them and turn them back on — put this on the cutover checklist.
8. **Tool choice:**

| Volume / need | Tool |
|---|---|
| Small, one-off (< ~20k rows), business users | Import from Excel/CSV wizard |
| Reference/config data across environments | Configuration Migration Tool (`pac tool cmt`) |
| Repeatable, transformations, Power Query skills | Dataflows |
| Large, complex, delta loads, ETL team | KingswaySoft (SSIS) or Azure Data Factory |
| Very large via code | `CreateMultiple` / `UpdateMultiple` / `UpsertMultiple`, ExecuteMultiple batches |

9. **Trial loads** in a non-prod environment with full volume at least once; time it for the cutover plan.
10. **Reconcile** after each load: source count vs. loaded vs. rejected per table; sample 20 records end-to-end with a business user; spot-check sums (e.g. total outstanding balance). Completion: every table has `source = loaded + rejected (with reasons)`.

## Data protection

Migration files contain personal data. Keep extracts in approved storage only, never in git, chat, or personal drives; delete after sign-off. Migrate only what's needed and lawful to keep (Kenya Data Protection Act 2019 / the client's jurisdiction).

## Deliverables

Mapping document, cleansing report, load scripts/packages, cutover checklist (with timings), reconciliation report.
