---
type: llm
---

PASS if the reply fixes the trigger with at least one of Select columns, Filter rows, or trigger conditions, and explains how to stop the flow re-triggering on its own update (for example excluding the columns it writes, a guard flag, or a condition on the modifying user).
FAIL if the reply does not change the trigger configuration or does not address the loop.
