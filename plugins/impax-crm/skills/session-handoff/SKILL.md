---
name: session-handoff
description: "Writes a pickup note that compacts the current session so a fresh session or a colleague can continue the work: goal, state per environment, next action, decisions, open questions, and gotchas, with secrets and personal data redacted. Use when the user asks to hand off, park, or log where the work is, or is ending a session with work still in flight."
---

# Session Handoff

Inspired by Matt Pocock's MIT-licensed `handoff` skill and `capturing-session-handoffs` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master).

Write a handoff note that lets someone with **zero context** pick the work up and take the next action in under five minutes.

## Steps

1. **Gather facts, don't recall them.** Check the current git branch and status, the solution version you were working in, open tickets/DevOps items mentioned this session, and the environment(s) touched (Dev / Test / UAT / Prod). Completion: every claim in the note has a source you just checked.
2. **Write the note** with exactly these sections:
   - **Goal** — one sentence: what the work is for (client, ticket, outcome).
   - **State** — what is done, what is half-done, what is untouched. Name the environment for each.
   - **Next action** — the single first thing the next session should do, concrete enough to start without reading anything else.
   - **Decisions made** — and the reason for each, so they aren't re-litigated.
   - **Open questions** — for whom (client, functional lead, you).
   - **Gotchas** — anything that bit you (a flow turned off, a plugin step disabled for testing, a manual config not in the solution).
   - **References** — links/paths to tickets, specs, PRs, solution files. Reference them; don't copy their contents.
   - **Suggested skills** — which skills from this repo the next session should invoke.
3. **Redact.** No client secrets, connection strings, passwords, tokens, or customer personal data (names, phone numbers, ID numbers, M-Pesa references). Use placeholders.
4. **Save** to `handoffs/YYYY-MM-DD-<slug>.md` in the current repo if one exists (ask before committing it), otherwise the OS temp directory. Tell the user the path.

If the user passed an argument, treat it as what the next session will focus on and tailor the note to it.

**Manual changes warning:** if anything was changed directly in an environment and is *not* in a solution (e.g. a setting toggled in Prod, a disabled plugin step), list it under Gotchas in bold. These are the changes that get lost.
