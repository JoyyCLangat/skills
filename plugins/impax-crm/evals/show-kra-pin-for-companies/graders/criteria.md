---
type: llm
---

PASS if the reply recommends a business rule as the simplest option or provides JavaScript that uses formContext from the execution context to set visibility and the required level; any JavaScript must not use Xrm.Page.
FAIL if the reply uses the deprecated Xrm.Page or manipulates the DOM directly.
