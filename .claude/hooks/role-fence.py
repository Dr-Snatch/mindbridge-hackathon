#!/usr/bin/env python3
"""PreToolUse hook: enforces per-role file ownership in the mindbridge repo.

Reads tool input from stdin. If MB_ROLE is set and the target file is outside
the role's allowed prefixes, blocks the edit with an explanatory message.
Falls back to allowing the edit if MB_ROLE is unset or unknown — so anyone
working without a role (e.g. a teammate just exploring) is not blocked.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROLE_ALLOWLIST: dict[str, list[str]] = {
    "A": ["apps/api/", "packages/types/", "prisma/"],          # Fullstack Lead
    "B": ["apps/ai/"],                                          # AI Engineer
    "C": ["apps/mobile/", "apps/dashboard/"],                   # Frontend Engineer
    "D": ["packages/design-tokens/"],                           # Brand & UX Designer (specs live in vault, not repo)
    "E": [""],                                                   # Product & Pitch Lead — unrestricted
}

ALWAYS_ALLOWED_FILES = {
    ".gitignore",
}


def find_repo_root(start: Path) -> Path | None:
    p = start.resolve()
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    return None


def main() -> None:
    role = os.environ.get("MB_ROLE", "").upper().strip()
    if not role:
        sys.exit(0)
    if role not in ROLE_ALLOWLIST:
        print(f"role-fence: warning — MB_ROLE={role} unknown, allowing", file=sys.stderr)
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path:
        sys.exit(0)

    target = Path(file_path)
    if not target.is_absolute():
        target = Path.cwd() / target
    target = target.resolve()

    repo_root = find_repo_root(target.parent if target.parent.exists() else Path.cwd())
    if not repo_root:
        sys.exit(0)

    try:
        rel = target.relative_to(repo_root)
    except ValueError:
        sys.exit(0)

    rel_str = str(rel).replace("\\", "/")
    if rel_str in ALWAYS_ALLOWED_FILES:
        sys.exit(0)

    allowed = ROLE_ALLOWLIST[role]
    if any(prefix == "" or rel_str.startswith(prefix) for prefix in allowed):
        sys.exit(0)

    msg_lines = [
        f"role-fence: blocked write to '{rel_str}'.",
        f"You are MB_ROLE={role}. This file is outside your allowed folders:",
    ]
    for p in allowed:
        msg_lines.append(f"  - {p or '(unrestricted)'}")
    msg_lines.append("")
    msg_lines.append("If you genuinely need this change:")
    msg_lines.append("  1. open a task in 20-tasks/ asking the file's owner to make the edit, OR")
    msg_lines.append("  2. escalate via 50-flags/ to Role E.")
    msg_lines.append("")
    msg_lines.append("Owners: A=fullstack(api/types/prisma), B=ai-engineer(apps/ai), C=frontend(mobile+dashboard), D=designer(design-tokens), E=product-lead(everywhere)")

    print("\n".join(msg_lines), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
