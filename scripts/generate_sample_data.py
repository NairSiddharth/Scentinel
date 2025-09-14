#!/usr/bin/env python3
"""
Scentinel Sample Data Generator

Creates realistic test data for development and demonstration purposes.
Generates colognes with proper notes, classifications, and wear history.
"""

import sys
import os
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scentinel.database import Database


# Sample fragrance data for realistic generation
SAMPLE_FRAGRANCES = [
    ("Aventus", "Creed", ["bergamot", "blackcurrant", "apple", "pineapple", "rose", "birch", "musk", "oakmoss"], ["fresh", "fruity", "smoky"]),
    ("Bleu de Chanel", "Chanel", ["lemon", "bergamot", "grapefruit", "ginger", "cedar", "sandalwood", "incense"], ["fresh", "woody", "aromatic"]),
    ("Sauvage", "Dior", ["calabrian bergamot", "pepper", "sichuan pepper", "lavender", "ambroxan", "cedar"], ["fresh", "spicy", "woody"]),
    ("Tom Ford Oud Wood", "Tom Ford", ["rosewood", "cardamom", "sandalwood", "oud", "rose", "vanilla", "amber"], ["woody", "oriental", "luxurious"]),
    ("Acqua di Gio", "Giorgio Armani", ["lime", "lemon", "bergamot", "jasmine", "rose", "cedar", "musk", "amber"], ["fresh", "aquatic", "citrus"]),
    ("One Million", "Paco Rabanne", ["grapefruit", "mint", "rose", "cinnamon", "spices", "amber", "leather", "wood"], ["spicy", "sweet", "aromatic"]),
    ("Terre d'Hermes", "Hermès", ["orange", "grapefruit", "pepper", "pelargonium", "flint", "cedar", "benzoin", "vetiver"], ["woody", "spicy", "mineral"]),
    ("Stronger With You", "Giorgio Armani", ["cardamom", "pink pepper", "violet leaf", "sage", "chestnut", "cedar", "vanilla", "amber"], ["spicy", "sweet", "warm"]),
    ("The One", "Dolce & Gabbana", ["bergamot", "coriander", "basil", "cardamom", "orange blossom", "ginger", "cedar", "amber"], ["spicy", "oriental", "warm"]),
    ("Invictus", "Paco Rabanne", ["grapefruit", "mandarin", "marine accord", "jasmine", "bay leaf", "patchouli", "ambergris", "guaiac wood"], ["fresh", "aquatic", "woody"]),
    ("Light Blue", "Dolce & Gabbana", ["lemon", "apple", "cedar", "bellflower", "bamboo", "jasmine", "white rose", "cedar", "amber", "musk"], ["fresh", "floral", "citrus"]),
    ("Polo Blue", "Ralph Lauren", ["cucumber", "mandarin", "basil", "sage", "geranium", "suede", "sheer musk", "woodsy notes"], ["fresh", "aquatic", "green"]),
    ("Luna Rossa", "Prada", ["lavender", "bitter orange", "mint", "clary sage", "spearmint", "ambroxan", "ambrette"], ["fresh", "aromatic", "citrus"]),
    ("Versace Eros", "Versace", ["mint", "lemon", "green apple", "tonka bean", "geranium", "ambroxan", "vanilla", "vetiver", "oakmoss"], ["fresh", "sweet", "woody"]),
    ("YSL L'Homme", "Yves Saint Laurent", ["bergamot", "lemon", "ginger", "spices", "violet leaf", "white pepper", "cedar", "tahitian vetiver"], ["fresh", "spicy", "woody"]),
    ("Montblanc Legend", "Montblanc", ["bergamot", "lavender", "pineapple leaf", "geranium", "coumarin", "apple", "rose", "dry wood", "tonka bean"], ["fresh", "aromatic", "woody"]),
    ("Armani Code", "Giorgio Armani", ["lemon", "bergamot", "anise", "olive flower", "star anise", "guaiac wood", "leather", "tobacco"], ["spicy", "woody", "warm"]),
    ("Cool Water", "Davidoff", ["peppermint", "lavender", "coriander", "geranium", "neroli", "sandalwood", "cedar", "musk", "amber"], ["fresh", "aquatic", "aromatic"]),
    ("Jean Paul Gaultier Le Male", "Jean Paul Gaultier", ["mint", "lavender", "cardamom", "bergamot", "cinnamon", "orange blossom", "sandalwood", "cedar", "tonka bean", "amber"], ["aromatic", "spicy", "sweet"]),
    ("Burberry Brit", "Burberry", ["green mandarin", "bergamot", "cardamom", "ginger", "wild rose", "nutmeg", "cedar", "grey musk"], ["fresh", "spicy", "woody"])
]

ADDITIONAL_NOTES = [
    "bergamot", "lemon", "lime", "orange", "grapefruit", "mandarin",
    "lavender", "rosemary", "sage", "basil", "mint", "eucalyptus",
    "rose", "jasmine", "ylang-ylang", "geranium", "violet", "iris",
    "cedar", "sandalwood", "vetiver", "patchouli", "oakmoss", "pine",
    "vanilla", "amber", "musk", "tonka bean", "benzoin", "labdanum",
    "pepper", "cardamom", "cinnamon", "nutmeg", "clove", "ginger",
    "leather", "tobacco", "smoke", "incense", "oud", "ambergris"
]

ADDITIONAL_CLASSIFICATIONS = [
    "fresh", "citrus", "floral", "woody", "oriental", "spicy",
    "aquatic", "green", "fruity", "gourmand", "smoky", "leathery",
    "powdery", "metallic", "animalic", "resinous", "herbal", "aromatic"
]

SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
OCCASIONS = ["Casual", "Work", "Date Night", "Special Event", "Gym", "Travel", "Evening"]


def create_sample_colognes(db: Database, count: int) -> List[Tuple[str, str]]:
    """Create sample cologne entries."""
    created = []

    # First add the predefined samples
    for name, brand, notes, classifications in SAMPLE_FRAGRANCES[:count]:
        try:
            db.add_cologne(name, brand, notes, classifications)
            created.append((brand, name))
            print(f"  ✓ Added: {brand} - {name}")
        except Exception as e:
            print(f"  ⚠ Skipped {brand} - {name}: {str(e)}")

    # If we need more, generate random ones
    remaining = count - len(created)
    if remaining > 0:
        print(f"\nGenerating {remaining} additional random fragrances...")

        for i in range(remaining):
            try:
                # Generate random fragrance
                brand = f"Brand {random.randint(1, 100)}"
                name = f"Fragrance {random.randint(1, 1000)}"

                # Random notes (3-8 notes)
                note_count = random.randint(3, 8)
                notes = random.sample(ADDITIONAL_NOTES, note_count)

                # Random classifications (1-4 classifications)
                class_count = random.randint(1, 4)
                classifications = random.sample(ADDITIONAL_CLASSIFICATIONS, class_count)

                db.add_cologne(name, brand, notes, classifications)
                created.append((brand, name))
                print(f"  ✓ Generated: {brand} - {name}")

            except Exception as e:
                print(f"  ✗ Failed to create random fragrance: {str(e)}")

    return created


def create_sample_wear_history(db: Database, cologne_list: List[Tuple[str, str]], wear_count: int) -> None:
    """Create realistic wear history for colognes."""
    print(f"\nGenerating {wear_count} wear history entries...")

    # Get cologne IDs
    cologne_ids = []
    for brand, name in cologne_list:
        cologne = db.get_cologne_by_name_and_brand(name, brand)
        if cologne:
            cologne_ids.append(cologne.id)

    if not cologne_ids:
        print("  ⚠ No colognes found to create wear history for")
        return

    created_count = 0
    for _ in range(wear_count):
        try:
            # Random cologne
            cologne_id = random.choice(cologne_ids)

            # Random date within last year
            days_ago = random.randint(1, 365)
            wear_date = datetime.now() - timedelta(days=days_ago)

            # Random rating (weighted towards higher ratings)
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]

            # Random season and occasion
            season = random.choice(SEASONS)
            occasion = random.choice(OCCASIONS)

            # Optional notes (30% chance)
            notes = None
            if random.random() < 0.3:
                note_options = [
                    "Love this for work!", "Perfect for date night", "Great longevity",
                    "Very fresh", "Too strong", "Subtle and nice", "Compliments magnet",
                    "Good for summer", "Winter beast", "Versatile fragrance",
                    "Unique scent", "Classic choice", "Modern twist"
                ]
                notes = random.choice(note_options)

            db.add_wear_history(cologne_id, wear_date, rating, season, occasion, notes)
            created_count += 1

            if created_count % 50 == 0:
                print(f"  ✓ Created {created_count} wear entries...")

        except Exception as e:
            print(f"  ✗ Failed to create wear entry: {str(e)}")

    print(f"  ✅ Created {created_count} total wear history entries")


def generate_sample_data(cologne_count: int, wear_count: int, clear_existing: bool = False) -> None:
    """Generate complete sample dataset."""
    try:
        db = Database()

        if clear_existing:
            print("🗑️ Clearing existing data...")
            # Clear tables in proper order (FK constraints)
            from sqlalchemy import text
            db.session.execute(text("DELETE FROM wear_history"))
            db.session.execute(text("DELETE FROM cologne_notes"))
            db.session.execute(text("DELETE FROM cologne_classifications"))
            db.session.execute(text("DELETE FROM colognes"))
            db.session.execute(text("DELETE FROM fragrance_notes"))
            db.session.execute(text("DELETE FROM scent_classifications"))
            db.session.commit()
            print("  ✓ Existing data cleared")

        print(f"\n🌟 Generating sample data:")
        print(f"  - Colognes: {cologne_count}")
        print(f"  - Wear entries: {wear_count}")

        # Create colognes
        print(f"\nCreating {cologne_count} cologne entries...")
        created_colognes = create_sample_colognes(db, cologne_count)

        if not created_colognes:
            print("✗ No colognes were created")
            return

        # Create wear history
        if wear_count > 0:
            create_sample_wear_history(db, created_colognes, wear_count)

        print(f"\n✅ Sample data generation completed!")
        print(f"  - {len(created_colognes)} colognes created")
        if wear_count > 0:
            print(f"  - Wear history generated")
        print(f"  - Database ready for testing")

    except Exception as e:
        print(f"✗ Sample data generation failed: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Scentinel Sample Data Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_sample_data.py --colognes 10 --wears 100
  python scripts/generate_sample_data.py --colognes 20 --wears 500 --clear
  python scripts/generate_sample_data.py --colognes 5 --wears 0  # Just colognes, no wear history
        """
    )

    parser.add_argument('--colognes', type=int, default=10,
                       help='Number of cologne entries to create (default: 10)')
    parser.add_argument('--wears', type=int, default=100,
                       help='Number of wear history entries to create (default: 100)')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing data before generating new data')

    args = parser.parse_args()

    if args.colognes < 0 or args.wears < 0:
        print("✗ Counts must be non-negative")
        sys.exit(1)

    generate_sample_data(args.colognes, args.wears, args.clear)


if __name__ == '__main__':
    main()