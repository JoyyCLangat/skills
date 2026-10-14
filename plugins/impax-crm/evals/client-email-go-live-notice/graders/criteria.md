---
type: llm
---

PASS if the reply contains a draft email with the date, a time window with a timezone (EAT or similar), what users should expect or do, and a contact for questions, and does not claim the email was sent.
FAIL if the reply omits the time window or timezone, invents commitments not in the prompt, or says the email was sent.
