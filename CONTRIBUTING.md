# Contributing

## Before opening a pull request

- Run `python -m py_compile scripts/create_issue.py`.
- Run a dry run without `--confirm`.
- Keep `.env`, API tokens, real Plane URLs, project UUIDs and personal paths out of the diff.
- Update the documentation when behavior changes.

## Scope

Keep the integration small and auditable. New dependencies, background services and remote infrastructure require a clear reason and documentation.
