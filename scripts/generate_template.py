#!/usr/bin/env python3
"""
Scentinel Template Generator
Generate empty JSON templates for cologne import with custom number of slots.

Usage:
    python generate_template.py 100                    # 100 empty slots
    python generate_template.py 50 --with-examples     # 5 examples + 45 empty
    python generate_template.py 25 --output custom.json # Custom filename
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

def create_empty_cologne(cologne_id: int) -> Dict[str, Any]:
    """Create an empty cologne template entry"""
    return {
        "id": cologne_id,
        "name": "",
        "brand": "",
        "notes": [],
        "classifications": [],
        "wear_history": []
    }

def create_example_cologne(cologne_id: int, name: str, brand: str, notes: List[str],
                          classifications: List[str], wear_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Create a cologne entry with example data"""
    return {
        "id": cologne_id,
        "name": name,
        "brand": brand,
        "notes": notes,
        "classifications": classifications,
        "wear_history": wear_history or []
    }

def get_example_colognes() -> List[Dict[str, Any]]:
    """Get list of example cologne entries"""
    examples = [
        {
            "name": "Bleu de Chanel",
            "brand": "Chanel",
            "notes": ["bergamot", "lemon", "cedar", "sandalwood", "ginger", "nutmeg"],
            "classifications": ["fresh", "woody", "aromatic"],
            "wear_history": [
                {
                    "date": "2024-09-10T08:00:00",
                    "season": "fall",
                    "occasion": "work",
                    "rating": 4.5
                }
            ]
        },
        {
            "name": "Sauvage",
            "brand": "Dior",
            "notes": ["bergamot", "pepper", "lavender", "vetiver", "cedar"],
            "classifications": ["fresh", "spicy", "aromatic"],
            "wear_history": [
                {
                    "date": "2024-09-08T14:00:00",
                    "season": "fall",
                    "occasion": "casual",
                    "rating": 4.0
                }
            ]
        },
        {
            "name": "Tom Ford Oud Wood",
            "brand": "Tom Ford",
            "notes": ["oud", "rosewood", "cardamom", "sandalwood", "vanilla", "amber"],
            "classifications": ["woody", "oriental", "luxury"],
            "wear_history": []
        },
        {
            "name": "Acqua di Gio",
            "brand": "Giorgio Armani",
            "notes": ["bergamot", "lime", "lemon", "jasmine", "cedar", "white musk"],
            "classifications": ["fresh", "aquatic", "citrus"],
            "wear_history": []
        },
        {
            "name": "Creed Aventus",
            "brand": "Creed",
            "notes": ["pineapple", "bergamot", "apple", "birch", "patchouli", "vanilla"],
            "classifications": ["fruity", "woody", "smoky", "luxury"],
            "wear_history": []
        }
    ]

    result = []
    for i, example in enumerate(examples, 1):
        result.append(create_example_cologne(
            i, example["name"], example["brand"],
            example["notes"], example["classifications"],
            example.get("wear_history", [])
        ))

    return result

def generate_template(count: int, with_examples: bool = False, output_file: Optional[str] = None) -> str:
    """Generate a cologne template JSON file"""

    # Create base structure
    template = {
        "export_date": datetime.now().isoformat(),
        "version": "1.0",
        "colognes": []
    }

    cologne_id = 1

    # Add examples if requested
    if with_examples:
        examples = get_example_colognes()
        template["colognes"].extend(examples)
        cologne_id = len(examples) + 1
        count = count - len(examples)  # Subtract examples from total count

        if count <= 0:
            count = 0  # Don't add empty slots if examples fill the requirement

    # Add empty cologne slots
    for i in range(count):
        template["colognes"].append(create_empty_cologne(cologne_id + i))

    # Generate filename if not provided
    if not output_file:
        total_slots = len(template["colognes"])
        if with_examples:
            output_file = f"cologne_template_{total_slots}_with_examples.json"
        else:
            output_file = f"cologne_template_{total_slots}.json"

    # Write to file
    output_path = Path("data") / output_file
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    return str(output_path)

def main():
    parser = argparse.ArgumentParser(
        description="Generate Scentinel cologne import templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_template.py 100                     # 100 empty slots
  python generate_template.py 50 --with-examples      # 5 examples + 45 empty slots
  python generate_template.py 25 --output my_colognes.json  # Custom filename
  python generate_template.py 10 --with-examples --output starter.json
        """
    )

    parser.add_argument("count", type=int, help="Number of cologne slots to generate")
    parser.add_argument("--with-examples", action="store_true",
                       help="Include 5 example colognes with real data")
    parser.add_argument("--output", "-o", help="Output filename (default: auto-generated)")

    args = parser.parse_args()

    if args.count < 1:
        print("❌ Error: Count must be at least 1")
        return 1

    if args.with_examples and args.count < 5:
        print("⚠️  Warning: With examples, minimum recommended count is 5")
        print("    (5 examples will be included, no empty slots)")

    try:
        output_path = generate_template(args.count, args.with_examples, args.output)

        total_colognes = args.count
        if args.with_examples:
            examples_count = min(5, args.count)
            empty_count = max(0, args.count - 5)
            print(f"✅ Generated template: {output_path}")
            print(f"   📋 {total_colognes} total slots")
            print(f"   🎯 {examples_count} example colognes")
            print(f"   ⭕ {empty_count} empty slots")
        else:
            print(f"✅ Generated template: {output_path}")
            print(f"   📋 {total_colognes} empty cologne slots")

        print(f"\n💡 Next steps:")
        print(f"   1. Edit {output_path} and fill in your cologne data")
        print(f"   2. Open Scentinel → Settings → Import Collection")
        print(f"   3. Upload your completed JSON file")

    except Exception as e:
        print(f"❌ Error generating template: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())