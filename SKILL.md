---
name: plane-backlog
description: Register ideas, pending work and future tasks in the correct Backlog project in self-hosted Plane without implementing them.
---

# Plane Backlog Capture

Use this skill when the user explicitly asks to register, save or queue an idea or future task in the Plane backlog without implementing it now.

1. Identify the active repository using its actual filesystem path. Do not guess from conversation titles.
2. Summarize the idea into a specific title and useful implementation context, including motivation, module and acceptance criteria when known. Do not invent requirements.
3. Call `scripts/create_issue.py` with `--project-path`, `--title`, `--description` and `--confirm` after the user requests registration. For dry-run validation, omit `--confirm`.
4. If the path is unmapped, ask for mapping rather than sending to another project.
5. Report the returned issue ID and state; only report a URL if the script returned one.
6. Never implement the captured idea unless separately instructed.
7. Never print, log or commit `PLANE_API_KEY`.

## Issue naming convention

Use `type(scope): concise description` with one of: `feat`, `fix`, `bug`, `idea`, `refactor`, `perf`, `docs`, `style`, `test`, `chore` or `security`.

Titles should be concise, use Brazilian Portuguese and never duplicate an existing prefix. If the scope is unclear, use `type: description`.
