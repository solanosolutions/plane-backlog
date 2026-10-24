#!/usr/bin/env python3
"""Register a work item in the correct self-hosted Plane project backlog."""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TYPES = {"feat", "fix", "bug", "idea", "refactor", "perf", "docs", "style", "test", "chore", "security"}
TITLE_PATTERN = re.compile(r"^([a-z]+)(?:\(([a-z0-9][a-z0-9._-]*)\))?:\s+(.+)$")


def load_env():
    """Load local settings without overwriting existing environment variables."""
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in {"PLANE_BASE_URL", "PLANE_WORKSPACE", "PLANE_API_KEY"}:
            os.environ.setdefault(key, value)


def validate_title(title):
    normalized = title.strip()
    match = TITLE_PATTERN.fullmatch(normalized)
    if not match:
        raise ValueError("Invalid title. Expected: type(scope): description or type: description.")
    issue_type, _scope, description = match.groups()
    if issue_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported issue type: {issue_type}")
    if not description.strip():
        raise ValueError("Issue description cannot be empty.")
    return normalized


def api(base, key, path, method="GET", payload=None):
    url = base.rstrip("/") + "/api/v1/" + path.lstrip("/")
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url, data=data, method=method,
        headers={"X-API-Key": key, "Accept": "application/json", "Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def resolve_project(project_path, mapping):
    current = Path(project_path).expanduser().resolve()
    matches = []
    for project in mapping["projects"]:
        for folder in project.get("paths", []):
            parent = Path(folder).expanduser().resolve()
            if current == parent or parent in current.parents:
                matches.append((len(parent.parts), project))
    if not matches:
        raise ValueError("Project path not mapped. Add it to config/projects.json; no issue created.")
    matches.sort(key=lambda item: item[0], reverse=True)
    if len(matches) > 1 and matches[0][0] == matches[1][0]:
        raise ValueError("Ambiguous project mapping; no issue created.")
    return matches[0][1]


def main():
    parser = argparse.ArgumentParser(description="Register an idea in the correct Plane backlog")
    parser.add_argument("--project-path", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--priority", choices=["none", "urgent", "high", "medium", "low"], default="low")
    parser.add_argument("--confirm", action="store_true", help="Actually create the item")
    args = parser.parse_args()

    title = validate_title(args.title)
    load_env()
    base = os.environ.get("PLANE_BASE_URL", "http://localhost:8080")
    key = os.environ.get("PLANE_API_KEY")
    workspace = os.environ.get("PLANE_WORKSPACE", "your-workspace")
    if not key:
        parser.error("PLANE_API_KEY environment variable is required")

    mapping = json.loads((ROOT / "config" / "projects.json").read_text(encoding="utf-8-sig"))
    project = resolve_project(args.project_path, mapping)
    prefix = f"workspaces/{urllib.parse.quote(workspace, safe='')}/projects/{project['id']}/"
    states_response = api(base, key, prefix + "states/")
    states = states_response.get("results", []) if isinstance(states_response, dict) else states_response
    backlog = [state for state in states if state.get("group") == "backlog"]
    if len(backlog) != 1:
        raise ValueError("Expected exactly one backlog state; no issue created.")

    description_html = "<p>" + html.escape(args.description).replace("\n", "<br>") + "</p>"
    body = {"name": title, "description_html": description_html, "priority": args.priority, "state_id": backlog[0]["id"]}
    if not args.confirm:
        print(json.dumps({"dry_run": True, "project": project["name"], "payload": body}, ensure_ascii=False, indent=2))
        return

    created = api(base, key, prefix + "work-items/", "POST", body)
    item_id = created["id"]
    verified = api(base, key, prefix + f"work-items/{item_id}/")
    if verified.get("state") != backlog[0]["id"]:
        raise RuntimeError(f"Item created ({item_id}) but backlog state could not be verified")
    sequence = verified.get("sequence_id")
    url = f"{base.rstrip('/')}/{workspace}/browse/{project['identifier']}-{sequence}" if sequence is not None else None
    print(json.dumps({"created": True, "project": project["name"], "id": item_id, "title": verified.get("name"), "state": "backlog", "url": url}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, RuntimeError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
