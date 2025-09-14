#!/usr/bin/env python3
"""
Scentinel CSV Import Utility

Command-line tool to import cologne data from CSV files.
Extracted from main application for batch processing and automation.
"""

import sys
import os
import csv
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scentinel.database import Database


def validate_csv_headers(csv_path: str) -> bool:
    """Validate that CSV has required headers."""
    required_headers = ['name', 'brand']
    optional_headers = ['notes', 'classifications']

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

            missing_required = [h for h in required_headers if h not in headers]
            if missing_required:
                print(f"✗ Missing required columns: {', '.join(missing_required)}")
                return False

            available_optional = [h for h in optional_headers if h in headers]
            print(f"✓ Found columns: {', '.join(headers)}")
            if available_optional:
                print(f"  Optional columns available: {', '.join(available_optional)}")

            return True

    except Exception as e:
        print(f"✗ Error reading CSV: {str(e)}")
        return False


def import_csv(csv_path: str, dry_run: bool = False) -> None:
    """Import cologne data from CSV file."""
    try:
        if not os.path.exists(csv_path):
            print(f"✗ File not found: {csv_path}")
            sys.exit(1)

        if not validate_csv_headers(csv_path):
            sys.exit(1)

        db = Database()
        added_count = 0
        skipped_count = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, 1):
                name = row.get('name', '').strip()
                brand = row.get('brand', '').strip()

                if not name or not brand:
                    print(f"  ⚠ Row {row_num}: Skipping - missing name or brand")
                    skipped_count += 1
                    continue

                # Check if cologne already exists
                from src.scentinel.database import Cologne
                existing = db.session.query(Cologne).filter_by(name=name, brand=brand).first()

                if existing:
                    print(f"  ⚠ Row {row_num}: Skipping - already exists: {brand} - {name}")
                    skipped_count += 1
                    continue

                if dry_run:
                    print(f"  ✓ Would import: {brand} - {name}")
                    continue

                try:
                    notes = row.get('notes', '').split(';') if row.get('notes') else []
                    classifications = row.get('classifications', '').split(';') if row.get('classifications') else []

                    # Clean up empty strings
                    notes = [n.strip() for n in notes if n.strip()]
                    classifications = [c.strip() for c in classifications if c.strip()]

                    db.add_cologne(name, brand, notes, classifications)
                    print(f"  ✓ Added: {brand} - {name}")
                    added_count += 1

                except Exception as e:
                    print(f"  ✗ Row {row_num}: Failed to add {brand} - {name}: {str(e)}")
                    skipped_count += 1

        if dry_run:
            print(f"\n📋 Dry run completed - no data was imported")
        else:
            print(f"\n✅ Import completed!")
            print(f"  - Added: {added_count} colognes")
            if skipped_count > 0:
                print(f"  - Skipped: {skipped_count} rows")

    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        sys.exit(1)


def create_sample_csv(output_path: str) -> None:
    """Create a sample CSV file with proper format."""
    sample_data = [
        {
            'name': 'Aventus',
            'brand': 'Creed',
            'notes': 'bergamot;blackcurrant;apple;pineapple;rose;birch;musk;oakmoss',
            'classifications': 'fresh;fruity;smoky'
        },
        {
            'name': 'Bleu de Chanel',
            'brand': 'Chanel',
            'notes': 'lemon;bergamot;grapefruit;ginger;cedar;sandalwood;incense',
            'classifications': 'fresh;woody;aromatic'
        },
        {
            'name': 'Sauvage',
            'brand': 'Dior',
            'notes': 'calabrian bergamot;pepper;sichuan pepper;lavender;ambroxan;cedar',
            'classifications': 'fresh;spicy;woody'
        }
    ]

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'brand', 'notes', 'classifications'])
            writer.writeheader()
            writer.writerows(sample_data)

        print(f"✓ Sample CSV created: {output_path}")

    except Exception as e:
        print(f"✗ Failed to create sample CSV: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Scentinel CSV Import Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format:
  Required columns: name, brand
  Optional columns: notes, classifications

  Notes and classifications should be semicolon-separated.

Examples:
  python scripts/import_csv.py data.csv
  python scripts/import_csv.py data.csv --dry-run
  python scripts/import_csv.py --create-sample sample.csv
        """
    )

    parser.add_argument('csv_file', nargs='?', help='CSV file to import')
    parser.add_argument('--dry-run', action='store_true', help='Preview import without making changes')
    parser.add_argument('--create-sample', metavar='FILE', help='Create a sample CSV file')

    args = parser.parse_args()

    if args.create_sample:
        create_sample_csv(args.create_sample)
    elif args.csv_file:
        import_csv(args.csv_file, args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()