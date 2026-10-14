---
name: dynamics-plugin-development
description: Write, register, debug, and test C# plugins and custom APIs for Dynamics 365 / Dataverse — execution pipeline stages, pre/post images, filtering attributes, depth and recursion, tracing, sandbox limits, plugin packages, and unit testing. Use when the user is writing or reviewing a plugin, registering a step in the Plugin Registration Tool, creating a Custom API, or deciding between a plugin and a flow.
---

# Dynamics Plugin Development

## Plugin or not?

| Use a plugin when | Use something else when |
|---|---|
| Logic must run **synchronously inside the transaction** (validate and block a save, set values before save, keep data consistent). | It's simple field logic on a form → **business rule** / JavaScript. |
| It must run for **every** channel (UI, API, import, integration). | It's async, notification-like, or calls many connectors → **Power Automate**. |
| Performance-critical, high-volume. | Business users must maintain it → flow. |

## Pipeline stages

| Stage | Value | Use for |
|---|---|---|
| PreValidation | 10 | Validation before security checks/transaction; cheap rejects. |
| PreOperation | 20 | **Change the Target** before it's saved (no extra Update call needed). |
| PostOperation | 40 | Actions after save (create related records). Sync = in transaction; async = after. |

## Skeleton

```csharp
using System;
using Microsoft.Xrm.Sdk;

public class AccountPreUpdate : IPlugin
{
    public void Execute(IServiceProvider serviceProvider)
    {
        var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
        var tracing = (ITracingService)serviceProvider.GetService(typeof(ITracingService));
        var factory = (IOrganizationServiceFactory)serviceProvider.GetService(typeof(IOrganizationServiceFactory));
        var service = factory.CreateOrganizationService(context.UserId);

        if (context.Depth > 1) return;   // guard only if recursion is actually possible; document why
        if (!(context.InputParameters["Target"] is Entity target)) return;

        tracing.Trace("AccountPreUpdate start {0}", target.Id);
        var pre = context.PreEntityImages.Contains("pre") ? context.PreEntityImages["pre"] : null;

        try
        {
            // business logic
        }
        catch (InvalidPluginExecutionException) { throw; }
        catch (Exception ex)
        {
            tracing.Trace(ex.ToString());
            throw new InvalidPluginExecutionException("Could not update the account. Contact support.", ex);
        }
    }
}
```

## Rules

- **Stateless.** No instance or static fields holding data — plugin instances are cached and reused across threads.
- **Filtering attributes** on every Update step — otherwise it fires on every save.
- **Images** instead of retrieving: register a Pre/Post image with only the columns you need.
- **Retrieve only needed columns** — never `new ColumnSet(true)`.
- **2-minute sandbox timeout**; no long external calls in sync steps. Call external services from async steps or hand off to Azure (Service Bus / Function).
- **Messages users see** come from `InvalidPluginExecutionException` — make them human and actionable.
- **Trace generously** (`ITracingService`); it shows in the Plugin Trace Log when enabled.
- **Running user**: `context.UserId` respects the caller's security; `CreateOrganizationService(null)` runs as SYSTEM — use deliberately and comment why.
- **Dependencies**: plugin **packages** (`pac plugin init`, NuGet-based) for third-party DLLs instead of ILMerge. Classic assemblies must be strong-name signed.
- **Custom API** instead of custom actions for new callable operations (typed request/response, privileges).

## Register

Plugin Registration Tool (`pac tool prt`) or `pac plugin push` for updates. For each step record: message, table, stage, mode, filtering attributes, images, run-in-user context, execution order — put this in the ticket. Add the assembly/package **and steps** to the solution.

## Test

- Unit test with **FakeXrmEasy** (or a hand-rolled `IOrganizationService` mock): arrange Target/images, execute, assert on the Target or created records.
- Then test in Dev with tracing on; check the Plugin Trace Log and the user-facing error message.
- Test as a non-admin role.

## Review checklist

- [ ] Correct stage/mode; filtering attributes set; images instead of retrieves.
- [ ] No infinite loop (Update on the same record in Post stage triggering itself).
- [ ] No hard-coded GUIDs/URLs — environment variables or configuration table.
- [ ] Exceptions wrapped with a friendly message; tracing present.
- [ ] Handles missing/null attributes in Target (Update Target has only changed columns).
- [ ] Unit tests cover the happy path and one failure.
