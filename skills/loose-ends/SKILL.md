---
name: loose-ends
description: Sweep a work session for loose ends — follow-ups, debt, client questions, and half-decisions that surfaced but were never recorded — verify each is still real, then file the survivors. Use before closing out a heavy session, or when the user says "any loose ends", "what did we leave open", "wrap up".
---

# Loose Ends

Inspired by `loose-ends` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master), generalised away from Fizzy.

A verification pass, not a dump. Most "loose ends" from a long session are already resolved by the time you look.

## Steps

1. **Harvest.** Scan the whole session for: TODOs said aloud, "we'll come back to that", errors worked around, temporary changes (disabled plugin steps, turned-off flows, test data, elevated permissions, a user added to System Administrator), questions for the client, and decisions left as "probably".
2. **Verify each one** against the current state — the environment, the repo, the ticket. Classify:
   - **Resolved** — drop it, note why in one line.
   - **Still real** — keep it.
   - **Human call** — you can't tell; ask.
   Completion: every harvested item has a classification backed by something you checked.
3. **Revert temporary changes first.** Anything temporary that is still in place (test-only permissions, disabled steps, debug tracing set to "All") — list it at the top and offer to revert it now.
4. **File the survivors** where the team tracks work (Azure DevOps, Jira, Planner, a ticket comment — ask which if you don't know). One item per entry: title, context, the evidence, and the suggested next step. Draft them for approval before creating anything.
5. **Report** a short table: item → classification → where it was filed.
