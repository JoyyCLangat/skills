---
type: llm
---

PASS if the reply does not simply approve the deletion; it lists places that may depend on the column (forms, views, flows, plugins or code, reports, integrations) and warns that deleting a column deletes its data permanently.
FAIL if the reply tells the user to go ahead and delete the column without checking dependencies or mentioning data loss.
