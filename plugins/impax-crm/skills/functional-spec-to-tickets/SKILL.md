---
name: functional-spec-to-tickets
description: Convert agreed CRM requirements or a functional design into build-ready tickets (Azure DevOps / Jira user stories) with Dataverse design, acceptance criteria, and test notes — then review them from a technical-lead, functional-consultant, and end-user angle. Use when the user wants to groom requirements, write user stories, break a feature into tasks, or review tickets before the team builds them.
---

# Functional Spec → Tickets

Inspired by `grooming-architect` and `ticket-review` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master), re-written for CRM delivery.

A good ticket lets a developer or maker build it **without a meeting**, and lets a tester verify it **without the developer**.

## Steps

1. **Ground in the real system.** If you have access to the solution (unpacked solution in the repo, `pac` CLI, or Dataverse MCP), read the actual table/column names, existing forms, flows, and plugins. Don't invent schema names. Unknown → mark `TBC` and add a question.
2. **Slice vertically.** Each ticket delivers something a user can see and test (e.g. "Loan officer can capture a loan application and see its status"), not a layer ("create all tables").
3. **Write each ticket** with this template:

```markdown
## <Title — user-visible outcome>

**User story:** As a <role>, I want <capability> so that <outcome>.
**Requirement IDs:** R-012, R-013

### Design
- Tables/columns: `<prefix>_loanapplication.<prefix>_amount` (Currency, required) …
- Forms/views/BPF: …
- Automation: <business rule | flow | plugin | JS> — and why that one
- Security: roles that get C/R/W/D/Append/AppendTo and at what depth
- Integration: …
- Solution: <solution name>, publisher prefix `<prefix>`

### Acceptance criteria (Given / When / Then)
1. Given …, when …, then …

### Out of scope
### Test notes (data needed, roles to test as)
### Estimate: S / M / L (hours if the team uses them)
### Dependencies
```

4. **Review panel.** Re-read every ticket as three reviewers and fix what they'd flag:
   - **Technical lead** — right automation choice? Sync plugin where async would do? API limits, recursion, transactions? Is it in a solution?
   - **Functional consultant** — could this be out-of-the-box instead? Does it match the client's process and words?
   - **End user** — clicks, required fields, mobile use, what happens on error?
   Completion: each ticket has acceptance criteria that a tester can run without asking a question.
5. **Order** the tickets by dependency and produce a short build sequence.

Output tickets as markdown. If the user wants them created in Azure DevOps/Jira and a tool is available, draft first and create only after approval.
