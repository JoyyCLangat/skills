---
type: llm
---

PASS if the reply contains C# implementing IPlugin that runs synchronously in a pre-operation or pre-validation stage, throws InvalidPluginExecutionException with a user-friendly message, uses tracing, and mentions registration details such as filtering attributes or images.
FAIL if the reply uses a post-operation asynchronous step, or contains no error handling.
