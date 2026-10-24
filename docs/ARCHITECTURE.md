# Architecture

`plane-backlog` is a local agent skill for registering ideas and future work in the correct Backlog state of a self-hosted Plane project. It is a small HTTP client around the Plane API, not a long-running integration service.

```text
Agent runtime → SKILL.md + project path/title/description
             → create_issue.py
             → explicit mapping and unique Backlog state
             → dry-run or confirmed POST
             → GET and state verification
             → compact JSON result
```

## Trust boundaries

1. User input and agent prompts are untrusted.
2. The local skill directory and injected environment are operator-controlled.
3. Plane is the external system of record.

The script HTML-escapes descriptions before sending them to Plane and never executes issue text.

## Non-goals

- No daemon, queue or background worker.
- No n8n or TwentyCRM dependency.
- No semantic duplicate detection.
- No automatic project mapping mutation.
- No public exposure of the Plane API.
