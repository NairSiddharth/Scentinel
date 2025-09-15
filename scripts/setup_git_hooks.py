#!/usr/bin/env python3
"""
Setup Git hooks for automatic versioning
"""
import os
import shutil
import stat
from pathlib import Path

def setup_hooks():
    """Setup Git hooks for automatic versioning"""
    project_root = Path(__file__).parent.parent
    git_hooks_dir = project_root / ".git" / "hooks"
    project_hooks_dir = project_root / ".githooks"

    if not git_hooks_dir.exists():
        print("[ERROR] No .git directory found. Make sure you're in a Git repository.")
        return False

    # Copy pre-commit hook
    src_hook = project_hooks_dir / "pre-commit"
    dst_hook = git_hooks_dir / "pre-commit"

    if src_hook.exists():
        shutil.copy2(src_hook, dst_hook)

        # Make executable (Unix/Linux/Mac)
        if os.name != 'nt':  # Not Windows
            dst_hook.chmod(dst_hook.stat().st_mode | stat.S_IEXEC)

        print(f"[OK] Installed pre-commit hook: {dst_hook}")
        print("[SUCCESS] Automatic versioning is now enabled!")
        print("\n[INFO] How it works:")
        print("   - Every commit automatically bumps version based on changed files")
        print("   - Major: main.py, database schema, major algorithm changes")
        print("   - Minor: tab updates, database methods, recommender improvements")
        print("   - Patch: documentation, bug fixes, styling")
        print("\n[MANUAL] Manual commands:")
        print("   - python scripts/version_manager.py --auto")
        print("   - python scripts/version_manager.py --set 1.2.3")
        print("   - python scripts/version_manager.py --get")

        return True
    else:
        print(f"[ERROR] Source hook not found: {src_hook}")
        return False

if __name__ == "__main__":
    setup_hooks()