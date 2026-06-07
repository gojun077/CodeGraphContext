"""Path sandbox helpers for CLI and MCP tools."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List


def get_allowed_roots() -> List[Path]:
    """Return directories under which paths may be indexed or loaded."""
    roots: List[Path] = [Path.cwd().resolve()]

    env_roots = os.environ.get("CGC_ALLOWED_ROOTS", "")
    if env_roots:
        separator = ";" if os.name == "nt" else ":"
        for entry in env_roots.split(separator):
            entry = entry.strip()
            if entry:
                roots.append(Path(entry).resolve())

    return roots


def is_path_allowed(path: Path) -> bool:
    """True when *path* resolves under an allowed root."""
    resolved = path.resolve()
    for root in get_allowed_roots():
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False
