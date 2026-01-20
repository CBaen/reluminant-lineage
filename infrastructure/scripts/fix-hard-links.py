#!/usr/bin/env python3
"""
Hard Link Maintenance Script

Checks and fixes hard links between ~/.claude/ config files and the repo.
Windows hard links can break when files are edited (some editors create new files).

Usage:
    python fix-hard-links.py          # Check and report status
    python fix-hard-links.py --fix    # Fix broken links
"""

import os
import sys
import subprocess
from pathlib import Path

# Files that should be hard-linked
LINKED_FILES = [
    {
        "local": Path.home() / ".claude" / "CLAUDE.md",
        "repo": Path.home() / "projects" / "reluminant-lineage" / "infrastructure" / "config" / "CLAUDE.md",
    },
    {
        "local": Path.home() / ".claude" / "settings.json",
        "repo": Path.home() / "projects" / "reluminant-lineage" / "infrastructure" / "config" / "settings.json",
    },
    {
        "local": Path.home() / ".claude" / "INFRASTRUCTURE.md",
        "repo": Path.home() / "projects" / "reluminant-lineage" / "infrastructure" / "config" / "INFRASTRUCTURE.md",
    },
]


def get_inode(path: Path) -> int | None:
    """Get the inode (file ID) of a file. Same inode = same hard link."""
    try:
        return os.stat(path).st_ino
    except FileNotFoundError:
        return None


def check_hard_link(local: Path, repo: Path) -> dict:
    """Check if two files are hard-linked."""
    local_inode = get_inode(local)
    repo_inode = get_inode(repo)

    if local_inode is None:
        return {"status": "missing_local", "local": local, "repo": repo}
    if repo_inode is None:
        return {"status": "missing_repo", "local": local, "repo": repo}
    if local_inode == repo_inode:
        return {"status": "linked", "local": local, "repo": repo}
    else:
        return {"status": "broken", "local": local, "repo": repo}


def fix_hard_link(local: Path, repo: Path) -> bool:
    """Fix a broken hard link by syncing and re-linking."""
    try:
        # Determine which file is newer
        local_mtime = local.stat().st_mtime if local.exists() else 0
        repo_mtime = repo.stat().st_mtime if repo.exists() else 0

        if local_mtime > repo_mtime:
            # Local is newer - copy to repo first
            print(f"  Local is newer, copying to repo...")
            import shutil
            shutil.copy2(local, repo)

        # Remove local file
        if local.exists():
            local.unlink()

        # Create hard link using PowerShell
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                f"New-Item -ItemType HardLink -Path '{local}' -Target '{repo}'"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  Hard link created: {local.name}")
            return True
        else:
            print(f"  ERROR: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    fix_mode = "--fix" in sys.argv

    print("Hard Link Status Check")
    print("=" * 50)

    broken = []
    for file_pair in LINKED_FILES:
        result = check_hard_link(file_pair["local"], file_pair["repo"])
        name = file_pair["local"].name

        if result["status"] == "linked":
            print(f"[OK] {name} - linked correctly")
        elif result["status"] == "broken":
            print(f"[BROKEN] {name} - different files, link broken")
            broken.append(file_pair)
        elif result["status"] == "missing_local":
            print(f"[MISSING] {name} - missing from ~/.claude/")
            broken.append(file_pair)
        elif result["status"] == "missing_repo":
            print(f"[MISSING] {name} - missing from repo")

    if broken:
        print(f"\n{len(broken)} broken link(s) found.")
        if fix_mode:
            print("\nFixing broken links...")
            for file_pair in broken:
                print(f"\n{file_pair['local'].name}:")
                fix_hard_link(file_pair["local"], file_pair["repo"])
            print("\nDone. Run again without --fix to verify.")
        else:
            print("Run with --fix to repair.")
    else:
        print("\nAll hard links are intact.")


if __name__ == "__main__":
    main()
