#!/usr/bin/env python3
"""
Automatic version management for Scentinel based on Git changes
"""
import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

class VersionManager:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.version_file = self.project_root / "scentinel" / "data" / "version.json"

        # Version classification rules
        self.major_patterns = [
            r"scentinel/main\.py",
            r"scentinel/database\.py.*schema",  # Schema changes
            r"scentinel/recommender\.py.*algorithm",  # Major algorithm changes
        ]

        self.minor_patterns = [
            r"scentinel/tabs/.*\.py",  # Single tab changes
            r"scentinel/database\.py",  # General database changes
            r"scentinel/recommender\.py",  # Recommender improvements
        ]

        self.patch_patterns = [
            r".*\.md$",  # Documentation
            r".*\.txt$",  # Requirements, etc.
            r"scripts/.*",  # Utility scripts
            r".*\.css$",  # Styling
            r".*\.js$",   # Frontend scripts
        ]

    def load_current_version(self) -> Dict[str, int]:
        """Load current version from version.json"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                pass

        # Default version
        return {"major": 1, "minor": 0, "patch": 0}

    def save_version(self, version: Dict[str, int]):
        """Save version to version.json"""
        with open(self.version_file, 'w') as f:
            json.dump(version, f, indent=2)

    def get_version_string(self, version: Dict[str, int] = None) -> str:
        """Get version as string (e.g., 'v1.2.3')"""
        if version is None:
            version = self.load_current_version()
        return f"v{version['major']}.{version['minor']}.{version['patch']}"

    def get_changed_files(self, since_commit: str = "HEAD~1") -> List[str]:
        """Get list of changed files since last commit"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", since_commit, "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.SubprocessError:
            print("Warning: Could not get git diff. Make sure you're in a git repository.")

        return []

    def classify_changes(self, changed_files: List[str]) -> Tuple[str, List[str]]:
        """Classify changes as major, minor, or patch"""
        major_changes = []
        minor_changes = []
        patch_changes = []

        for file_path in changed_files:
            file_matched = False

            # Check for major changes
            for pattern in self.major_patterns:
                if re.search(pattern, file_path):
                    major_changes.append(file_path)
                    file_matched = True
                    break

            if file_matched:
                continue

            # Check for minor changes
            for pattern in self.minor_patterns:
                if re.search(pattern, file_path):
                    minor_changes.append(file_path)
                    file_matched = True
                    break

            if file_matched:
                continue

            # Check for patch changes
            for pattern in self.patch_patterns:
                if re.search(pattern, file_path):
                    patch_changes.append(file_path)
                    file_matched = True
                    break

            # If no pattern matched, default to minor
            if not file_matched:
                minor_changes.append(file_path)

        # Determine overall change level
        if major_changes:
            return "major", major_changes
        elif minor_changes:
            return "minor", minor_changes
        elif patch_changes:
            return "patch", patch_changes
        else:
            return "patch", []  # Default to patch for empty changes

    def increment_version(self, change_type: str) -> Dict[str, int]:
        """Increment version based on change type"""
        version = self.load_current_version()

        if change_type == "major":
            version["major"] += 1
            version["minor"] = 0
            version["patch"] = 0
        elif change_type == "minor":
            version["minor"] += 1
            version["patch"] = 0
        elif change_type == "patch":
            version["patch"] += 1

        return version

    def update_main_py_version(self, version: Dict[str, int]):
        """Update the APP_VERSION in main.py"""
        main_py_path = self.project_root / "scentinel" / "main.py"

        if not main_py_path.exists():
            print(f"Warning: {main_py_path} not found")
            return

        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update APP_VERSION line
            version_string = self.get_version_string(version)
            new_content = re.sub(
                r'APP_VERSION = "[^"]*"',
                f'APP_VERSION = "{version_string}"',
                content
            )

            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"Updated APP_VERSION to {version_string} in main.py")

        except Exception as e:
            print(f"Error updating main.py: {e}")

    def auto_version(self, since_commit: str = "HEAD~1") -> str:
        """Automatically version based on git changes"""
        changed_files = self.get_changed_files(since_commit)

        if not changed_files:
            print("No changes detected")
            return self.get_version_string()

        change_type, relevant_files = self.classify_changes(changed_files)
        new_version = self.increment_version(change_type)

        # Save new version
        self.save_version(new_version)

        # Update main.py
        self.update_main_py_version(new_version)

        version_string = self.get_version_string(new_version)

        print(f"Version bumped to {version_string}")
        print(f"Change type: {change_type.upper()}")
        print(f"Files that triggered this version:")
        for file_path in relevant_files:
            print(f"   - {file_path}")

        return version_string

    def manual_version(self, version_string: str):
        """Manually set version (e.g., 'v1.2.3' or '1.2.3')"""
        # Parse version string
        version_string = version_string.lstrip('v')
        parts = version_string.split('.')

        if len(parts) != 3:
            raise ValueError("Version must be in format 'major.minor.patch'")

        try:
            version = {
                "major": int(parts[0]),
                "minor": int(parts[1]),
                "patch": int(parts[2])
            }
        except ValueError:
            raise ValueError("Version parts must be integers")

        self.save_version(version)
        self.update_main_py_version(version)

        print(f"Manually set version to {self.get_version_string(version)}")
        return self.get_version_string(version)


def main():
    """CLI interface for version management"""
    import argparse

    parser = argparse.ArgumentParser(description="Scentinel Version Manager")
    parser.add_argument("--auto", action="store_true", help="Auto-version based on git changes")
    parser.add_argument("--set", type=str, help="Manually set version (e.g., '1.2.3')")
    parser.add_argument("--get", action="store_true", help="Get current version")
    parser.add_argument("--since", type=str, default="HEAD~1", help="Compare changes since this commit")

    args = parser.parse_args()

    vm = VersionManager()

    if args.auto:
        vm.auto_version(args.since)
    elif args.set:
        vm.manual_version(args.set)
    elif args.get:
        print(f"Current version: {vm.get_version_string()}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()