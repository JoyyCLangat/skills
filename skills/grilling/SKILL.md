---
name: grilling
description: Grill the user relentlessly about a plan, client requirement, solution design, or decision until there is a shared understanding. Use when the user wants to stress-test their thinking, says "grill me", or before committing to a CRM design or estimate.
---

# Grilling

Adapted from Matt Pocock's MIT-licensed [grilling](https://github.com/mattpocock/skills) skill, via [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master). Changed: CRM-specific prompts for the design tree.

Interview the user relentlessly until you reach a shared understanding. Map the topic as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard. Ask the whole frontier in one round, number each question, and give your recommended answer. Then wait.

```
❓ **Q1** - **<question title>**: <question body, including options if any>

➡️ <your recommended answer and why>
```

Each round reshapes the tree: settled decisions push the frontier outward. A question whose answer depends on another question still open this round belongs to a *later* round.

**Facts are your job, decisions are the user's.** If a question needs a fact you can look up (the solution's schema, an existing flow, Microsoft docs, the repo), look it up — don't ask. Put only the decisions to the user.

## CRM branches to make sure the tree covers

Visit whichever apply; skip the rest silently.

- **Out-of-the-box first** — does a standard Dynamics 365 / Dataverse feature already do this (business process flow, SLA, routing rules, duplicate detection, rollup column)? Customisation needs a reason.
- **Data model** — new table vs. existing; ownership (user/team vs. organisation); relationships and cascade behaviour; choice vs. lookup.
- **Who** — which security roles, business units, and teams see and edit it.
- **Automation home** — business rule, Power Automate flow, plugin, or JavaScript, and why that one (sync vs. async, transaction, licensing).
- **Integration** — which system is the source of truth for each field.
- **Volume and limits** — record counts, API request limits, flow run limits.
- **Licensing** — does the design push users onto a more expensive licence?
- **Deployment** — which solution, which publisher, how it moves Dev → Test → Prod.
- **Done** — what the client will check in UAT to sign it off.

Done when the frontier is empty: every branch visited, nothing silently assumed. Do not act on the result until the user confirms the shared understanding.
