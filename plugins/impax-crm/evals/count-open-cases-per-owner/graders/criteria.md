---
type: llm
---

PASS if the reply contains a FetchXML aggregate query (or an equivalent OData/TDS query) that counts cases grouped by owner and filters to open cases with statecode equal to 0.
FAIL if the reply has no query, or the query neither groups by owner nor filters to open cases.
