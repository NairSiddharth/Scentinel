#!/usr/bin/env python3
"""
Scentinel Image Cleanup Utility

Command-line tool to manage image storage, compression, and cleanup.
Extracted from photo_api.py for standalone image management.
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scentinel.photo_api import PhotoAPI


def show_storage_stats(api: PhotoAPI) -> None:
    """Display detailed storage statistics."""
    stats = api.get_storage_stats()

    print("📊 Storage Statistics:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
    print(f"  Storage path: {api.storage_path}")
    print(f"  Warning threshold: {api.max_collection_size_mb} MB")

    warning = api.get_collection_size_warning()
    if warning:
        print(f"\n{warning}")

    # Show size per image if we have images
    if stats['total_images'] > 0:
        avg_size = (stats['total_size_mb'] * 1024) / stats['total_images']
        print(f"  Average size per image: {avg_size:.1f} KB")


def cleanup_old_images(api: PhotoAPI, days_old: int, dry_run: bool = False) -> None:
    """Clean up images older than specified days."""
    try:
        if dry_run:
            print(f"🔍 Dry run: Finding images older than {days_old} days...")
        else:
            print(f"🧹 Cleaning up images older than {days_old} days...")

        # Get stats before cleanup
        before_stats = api.get_storage_stats()

        if dry_run:
            # Simulate cleanup without actually deleting
            cutoff_date = datetime.now() - timedelta(days=days_old)
            count = 0
            size_freed = 0

            for image_file in Path(api.storage_path).glob("*.jpg"):
                if image_file.stat().st_mtime < cutoff_date.timestamp():
                    size_mb = image_file.stat().st_size / (1024 * 1024)
                    print(f"  Would delete: {image_file.name} ({size_mb:.2f} MB)")
                    count += 1
                    size_freed += size_mb

            if count > 0:
                print(f"\n📋 Dry run results:")
                print(f"  Files to delete: {count}")
                print(f"  Space to free: {size_freed:.2f} MB")
            else:
                print(f"  No images older than {days_old} days found")
        else:
            # Actually perform cleanup
            api.cleanup_old_images(days_old)
            after_stats = api.get_storage_stats()

            files_deleted = before_stats['total_images'] - after_stats['total_images']
            space_freed = before_stats['total_size_mb'] - after_stats['total_size_mb']

            if files_deleted > 0:
                print(f"✅ Cleanup completed:")
                print(f"  Files deleted: {files_deleted}")
                print(f"  Space freed: {space_freed:.2f} MB")
                print(f"  Remaining: {after_stats['total_images']} images, {after_stats['total_size_mb']:.2f} MB")
            else:
                print(f"  No images older than {days_old} days found")

    except Exception as e:
        print(f"✗ Cleanup failed: {str(e)}")
        sys.exit(1)


def recompress_images(api: PhotoAPI, max_size_kb: int, dry_run: bool = False) -> None:
    """Recompress all images to a smaller size."""
    try:
        if dry_run:
            print(f"🔍 Dry run: Would recompress images to max {max_size_kb} KB...")
        else:
            print(f"🗜️ Recompressing images to max {max_size_kb} KB...")

        before_stats = api.get_storage_stats()
        processed = 0
        space_saved = 0

        for image_file in Path(api.storage_path).glob("*.jpg"):
            try:
                current_size_kb = image_file.stat().st_size // 1024

                if current_size_kb <= max_size_kb:
                    continue

                if dry_run:
                    potential_savings = current_size_kb - max_size_kb
                    print(f"  Would compress: {image_file.name} ({current_size_kb} KB → ~{max_size_kb} KB)")
                    space_saved += potential_savings
                    processed += 1
                else:
                    # Actually recompress the image
                    with open(image_file, 'rb') as f:
                        original_data = f.read()

                    compressed_data = api._compress_image(original_data, max_size_kb)

                    with open(image_file, 'wb') as f:
                        f.write(compressed_data)

                    new_size_kb = len(compressed_data) // 1024
                    savings = current_size_kb - new_size_kb
                    print(f"  ✓ Compressed: {image_file.name} ({current_size_kb} KB → {new_size_kb} KB)")
                    space_saved += savings
                    processed += 1

            except Exception as e:
                print(f"  ✗ Failed to process {image_file.name}: {str(e)}")

        if processed > 0:
            if dry_run:
                print(f"\n📋 Dry run results:")
                print(f"  Images to compress: {processed}")
                print(f"  Estimated space savings: ~{space_saved / 1024:.2f} MB")
            else:
                after_stats = api.get_storage_stats()
                actual_savings = before_stats['total_size_mb'] - after_stats['total_size_mb']
                print(f"\n✅ Recompression completed:")
                print(f"  Images processed: {processed}")
                print(f"  Space saved: {actual_savings:.2f} MB")
        else:
            print(f"  No images need recompression (all ≤ {max_size_kb} KB)")

    except Exception as e:
        print(f"✗ Recompression failed: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Scentinel Image Cleanup & Management Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/cleanup_images.py stats
  python scripts/cleanup_images.py cleanup --days 90
  python scripts/cleanup_images.py cleanup --days 30 --dry-run
  python scripts/cleanup_images.py recompress --size 80
  python scripts/cleanup_images.py recompress --size 50 --dry-run
        """
    )

    parser.add_argument('--storage-path', default='data/images',
                       help='Image storage directory (default: data/images)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Stats command
    subparsers.add_parser('stats', help='Show storage statistics')

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old images')
    cleanup_parser.add_argument('--days', type=int, default=90,
                               help='Delete images older than this many days (default: 90)')
    cleanup_parser.add_argument('--dry-run', action='store_true',
                               help='Preview cleanup without making changes')

    # Recompress command
    recompress_parser = subparsers.add_parser('recompress', help='Recompress images to smaller size')
    recompress_parser.add_argument('--size', type=int, default=80,
                                  help='Maximum size per image in KB (default: 80)')
    recompress_parser.add_argument('--dry-run', action='store_true',
                                  help='Preview recompression without making changes')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize PhotoAPI with custom storage path
    api = PhotoAPI(storage_path=args.storage_path)

    if not api.dependencies_available:
        print("✗ Missing dependencies: PIL/Pillow is required for image operations")
        print("  Install with: pip install Pillow")
        sys.exit(1)

    if args.command == 'stats':
        show_storage_stats(api)
    elif args.command == 'cleanup':
        cleanup_old_images(api, args.days, args.dry_run)
    elif args.command == 'recompress':
        recompress_images(api, args.size, args.dry_run)


if __name__ == '__main__':
    main()