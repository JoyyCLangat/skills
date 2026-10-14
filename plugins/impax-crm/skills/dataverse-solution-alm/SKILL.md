---
name: dataverse-solution-alm
description: Application lifecycle management for Dynamics 365 / Dataverse solutions — solution and publisher setup, managed vs unmanaged, segmentation, patches and upgrades, environment variables and connection references, source control with the pac CLI, and deployments Dev → Test/UAT → Prod (pipelines, Azure DevOps, GitHub Actions). Use when creating a solution, exporting/importing/unpacking solutions, setting up CI/CD, planning a deployment, or fixing a failed solution import.
---

# Dataverse Solution ALM

## Non-negotiables

- **Everything goes in a solution** with the company/client **publisher prefix** — never build in the Default Solution.
- **Unmanaged in Dev only. Managed everywhere else** (Test, UAT, Prod).
- **No direct edits in Prod.** If an emergency change happened, record it and back-port to Dev the same day.
- **Environment-specific values** (URLs, IDs, emails, API endpoints) live in **environment variables**; connections in **connection references**. Never hard-code them in flows, plugins, or JS.
- **Add only what you changed** when adding existing components (e.g. for Account, add only the new columns/forms — not "Include all objects"), to avoid overwriting other solutions' layers.

## Workflow: source-controlling a solution

```bash
pac auth create --name dev --environment https://<org>.crm4.dynamics.com
pac solution list
pac solution online-version --solution-name <Solution> --solution-version 1.4.0.0   # bump before export
pac solution export --name <Solution> --path out/<Solution>.zip --managed false
pac solution export --name <Solution> --path out/<Solution>_managed.zip --managed true
pac solution unpack --zipfile out/<Solution>.zip --folder src/<Solution> --packagetype Both
pac solution create-settings --solution-zip out/<Solution>.zip --settings-file config/<env>.settings.json
pac solution check --path out/<Solution>_managed.zip      # Solution Checker
```

Commit the unpacked folder (`src/`), not the zips. Fill one settings file per target environment (environment variable values + connection reference connection IDs) — **no secrets in git**; use pipeline secret variables or Azure Key Vault–backed environment variables.

Deploy:

```bash
pac solution pack --zipfile out/<Solution>_managed.zip --folder src/<Solution> --packagetype Managed
pac auth select --name uat
pac solution import --path out/<Solution>_managed.zip --settings-file config/uat.settings.json --async --activate-plugins
```

Automate with **Power Platform Pipelines** (in-product), **Power Platform Build Tools** (Azure DevOps), or **microsoft/powerplatform-actions** (GitHub). Ask which the team uses before proposing a new one.

## Versioning

`major.minor.build.revision`. Bump **minor** for a release, **build** for a hotfix. Version must increase for an upgrade to import.

## Import types (managed)

- **Upgrade** (default) — applies and **deletes components removed from the solution**. Data in deleted columns is gone.
- **Stage for upgrade** — lets you run data migration between the two steps.
- **Update** — overlays, never deletes. Leaves orphans.
- **Patches** — small fixes on a parent; they must be rolled up with *Clone solution* later. Most teams avoid patches and just ship a new version.

## Troubleshooting failed imports

| Error | Usual cause → fix |
|---|---|
| Missing dependency | Component references something not in the target (another solution, a column, a web resource). Read the missing component list; import the dependency first or add it. |
| Publisher prefix / layer conflict | Same component in two unmanaged layers or unmanaged customisation on top of managed in target. Check *Solution layers*; remove the unmanaged layer. |
| Connection reference / env var not set | Provide a settings file or set values after import, then turn flows on. |
| Flows off after import | Connection owner not set or the importing identity lacks access to the connection. Reassign and turn on. |
| Timeout on large solution | Use `--async`, split the solution (segment), or use a pipeline. |
| Plugin assembly version | Assembly major/minor change requires re-registration of steps; keep major.minor stable for plugin updates. |

## Segmentation (when one solution gets too big)

Split by layer: **Base** (tables, columns, choices, security roles) → **Logic** (plugins, flows, web resources) → **UI** (apps, forms, views, dashboards). Import in that order. Keep the same publisher.

## Checklist before any deployment

- [ ] Solution version bumped; Solution Checker has no critical issues.
- [ ] Settings file for the target environment is complete.
- [ ] Target backup taken (Prod: always).
- [ ] Manual post-steps listed (see `crm-release-notes`).
- [ ] Impact of any removed components assessed (`crm-impact-analysis`).
