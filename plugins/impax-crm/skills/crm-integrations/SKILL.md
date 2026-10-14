---
name: crm-integrations
description: "Designs and builds integrations between Dynamics 365 / Dataverse and other systems: ERPs (Business Central, Finance and Operations, Sage), core banking or insurance systems, M-Pesa (Daraja API), SMS gateways, websites and portals, using the Dataverse Web API with app registrations, webhooks, Azure Service Bus, Azure Functions, Logic Apps, Power Automate, virtual tables, or dual-write. Use when the user needs to sync data in or out of CRM, receive payment callbacks, choose an integration pattern, or debug an integration."
---

# CRM Integrations

## Step 1 — Pin the contract before choosing tech

For each data flow, answer (ask what you can't look up):

| Question | Example |
|---|---|
| Direction & trigger | ERP → CRM on invoice posted; CRM → SMS on case resolved |
| Source of truth per field | Credit limit: ERP. Phone number: CRM. |
| Volume & latency | 2k/day, within 5 min |
| Identity / matching key | Customer number (alternate key in CRM) |
| Failure handling | Retry? Dead-letter? Who is alerted? |
| Security | Auth method, network (IP allow-list, VPN), PII in payload |

Completion: one row per flow, no blanks.

## Step 2 — Pick the pattern

| Need | Pattern |
|---|---|
| Low volume, simple, connector exists | **Power Automate** (premium connector licensing!) |
| External system reads/writes CRM | **Dataverse Web API** with an **Entra ID app registration + application user** (client credentials / certificate), dedicated least-privilege role |
| CRM pushes events reliably | Plugin step → **Service Endpoint (Azure Service Bus)** or **webhook** registered in Plugin Registration Tool; consumer = Azure Function / Logic App |
| Inbound callbacks (e.g. M-Pesa) | **Azure Function** (HTTP) validates, de-duplicates, writes to Dataverse |
| Show external data without copying | **Virtual tables** |
| D365 Finance & Operations | **Dual-write** (or virtual entities) |
| Business Central | Built-in BC ↔ Dataverse integration / CRM connector |
| Bulk / scheduled sync | Azure Data Factory, KingswaySoft, or Dataflows |

## Rules

- **Upsert with alternate keys**, never by searching names. Store the external ID on the CRM record.
- **Idempotent** consumers — the same message twice must not create duplicates (key on the external transaction ID).
- **Secrets** in Azure Key Vault / environment variables of type Secret — never in code, flows, or git.
- **Respect API limits** — batch (`$batch`, `ExecuteMultiple`, `CreateMultiple`), back off on HTTP 429 using `Retry-After`.
- **Log every message** with correlation ID, status, and error to a log table or Application Insights; alert on failures.
- **Don't integrate as a named human user.**

## M-Pesa (Daraja) notes

Common flows: **STK Push** (Lipa na M-Pesa Online) to request payment from a customer, **C2B** confirmation/validation URLs for paybill/till payments, B2C for disbursements, transaction status query.

- Callback URLs must be public HTTPS → an Azure Function (or API Management) receives them, **not** Dataverse directly.
- Treat the M-Pesa receipt/transaction ID as the idempotency key; store it in a payment table with an alternate key.
- Match payments to CRM records by account reference (e.g. invoice/loan number); park unmatched payments in a review queue rather than guessing.
- Use Safaricom's sandbox for Dev/Test; production credentials per environment in Key Vault.
- Phone numbers go to Daraja as `254` plus the 9-digit subscriber number, with no `+` or leading `0` (`2547XXXXXXXX` or `2541XXXXXXXX`). Normalise and validate before sending.

Always confirm current endpoint details against Safaricom's Daraja documentation — don't rely on memory.

## SMS / WhatsApp

Through the client's gateway (e.g. Africa's Talking, Twilio, or a local aggregator) from a flow or Azure Function; record each message as an activity on the contact; respect opt-out and consent.

## Debugging

Follow `diagnosing-crm-issues`; check System Jobs for failed service-endpoint posts, Service Bus dead-letter queue, Function logs (Application Insights), the app user's role, and API limit headers.
