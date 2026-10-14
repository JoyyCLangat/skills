---
type: llm
---

PASS if the reply starts by gathering the exact error and comparing the user's security roles or context with the working user, proposes ranked hypotheses such as missing privileges or a plugin or flow error, and checks whether other users are affected before fixing.
FAIL if the reply jumps straight to a fix such as making the user an administrator without investigating.
