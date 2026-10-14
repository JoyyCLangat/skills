---
type: llm
---

PASS if the reply describes receiving M-Pesa callbacks through a public HTTPS endpoint such as an Azure Function, matching payments to records by an account reference, using the M-Pesa transaction ID to avoid duplicate payments, and keeping credentials out of code.
FAIL if the reply has no plan for duplicate callbacks or puts credentials directly in code.
