#!/usr/bin/env python3
"""
Scentinel Data Backup Utility

Command-line tool to export/import Scentinel data without running the GUI.
Extracted from main application for modularity.
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scentinel.database import Database


def export_data(output_file: str | None = None) -> str:
    """Export all data to JSON backup file."""
    try:
        db = Database()
        json_data = db.export_to_json()

        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"scentinel_backup_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)

        print(f"✓ Backup exported to: {output_file}")
        return output_file

    except Exception as e:
        print(f"✗ Export failed: {str(e)}")
        sys.exit(1)


def import_data(input_file: str) -> None:
    """Import data from JSON backup file."""
    try:
        if not os.path.exists(input_file):
            print(f"✗ File not found: {input_file}")
            sys.exit(1)

        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = f.read()

        db = Database()
        result = db.import_from_json(json_data)

        if result['success']:
            print(f"✓ Import successful!")
            print(f"  - Colognes added: {result['colognes_added']}")
            print(f"  - Wear records added: {result['wear_history_added']}")
            if result['colognes_skipped'] > 0:
                print(f"  - Colognes skipped (duplicates): {result['colognes_skipped']}")
        else:
            print(f"✗ Import failed: {result['error']}")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Scentinel Data Backup & Restore Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/backup_data.py export
  python scripts/backup_data.py export -o my_backup.json
  python scripts/backup_data.py import my_backup.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to backup file')
    export_parser.add_argument('-o', '--output', help='Output file path (default: timestamped filename)')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from backup file')
    import_parser.add_argument('file', help='JSON backup file to import')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'export':
        export_data(args.output)
    elif args.command == 'import':
        import_data(args.file)


if __name__ == '__main__':
    main()