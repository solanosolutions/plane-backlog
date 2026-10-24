# Security checklist

## Secrets

- Keep `.env` and real tokens out of Git.
- Inject `PLANE_API_KEY` through the agent session or a secrets manager.
- Do not include credentials, private hostnames, project UUIDs or personal paths in screenshots or issue descriptions.
- Rotate a token if it is exposed outside the approved secret store.

## Existing controls

- Explicit path mapping with longest-match preference.
- No write without `--confirm`.
- Exactly one `group=backlog` state required.
- POST followed by GET and state verification.
- HTML escaping for descriptions.
- No execution of issue text.

## Deployment

Use HTTPS for VPS deployments, preserve Plane IDs during migration, verify least-privilege project permissions and run a dry-run plus controlled create/GET check before changing agents to a new endpoint.
