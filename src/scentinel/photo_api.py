#!/usr/bin/env python3
"""
Photo API for Scentinel - Scrapes cologne bottle images from fragrance websites
with compression and storage management
"""

import os
import time
from typing import Optional, Dict, List, Tuple
from urllib.parse import urljoin, urlparse, quote
import hashlib
from io import BytesIO
import json
from datetime import datetime
import shutil

try:
    import requests
    from PIL import Image, ImageOps
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Missing dependencies for photo API: {e}")
    DEPENDENCIES_AVAILABLE = False
    requests = None  # type: ignore
    Image = None  # type: ignore
    ImageOps = None  # type: ignore


class PhotoAPI:
    def __init__(self, storage_path: str = "cologne_images"):
        self.storage_path = storage_path
        self.cache_file = os.path.join(storage_path, "image_cache.json")
        self.max_collection_size_mb = 100  # Warning threshold
        self.dependencies_available = DEPENDENCIES_AVAILABLE

        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)

        # Load cache
        self.cache = self._load_cache()

        # Headers to mimic browser requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _load_cache(self) -> Dict:
        """Load image cache from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"images": {}, "stats": {"total_size_mb": 0, "total_images": 0}}

    def _save_cache(self):
        """Save image cache to disk"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _generate_cache_key(self, cologne_name: str, brand: str) -> str:
        """Generate a unique cache key for cologne"""
        key = f"{brand}_{cologne_name}".lower().replace(" ", "_")
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def _get_storage_size(self) -> float:
        """Get total storage size in MB"""
        total_size = 0
        for root, dirs, files in os.walk(self.storage_path):
            for file in files:
                if file.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    total_size += os.path.getsize(os.path.join(root, file))
        return total_size / (1024 * 1024)  # Convert to MB

    def _compress_image(self, image_data: bytes, max_size_kb: int = 100) -> bytes:
        """Compress image to target size while maintaining quality"""
        if not self.dependencies_available or Image is None:
            raise Exception("PIL not available for image compression")

        img = Image.open(BytesIO(image_data))

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
            img = background

        # Resize if too large
        max_dimension = 400
        if max(img.size) > max_dimension:
            # Use LANCZOS resampling (available in older PIL versions too)
            try:
                # Try modern PIL first
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            except AttributeError:
                # Fallback for older PIL versions
                img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)  # type: ignore

        # Compress with different quality levels
        for quality in [85, 75, 65, 55]:
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_data = output.getvalue()

            if len(compressed_data) <= max_size_kb * 1024:
                return compressed_data

        # If still too large, return the smallest version
        return compressed_data

    def search_fragrantica(self, cologne_name: str, brand: str) -> Optional[str]:
        """Search for cologne image on Fragrantica"""
        if not self.dependencies_available or requests is None:
            return None

        try:
            # Create search query
            query = f"{brand} {cologne_name}".strip()
            search_url = f"https://www.fragrantica.com/search/"

            # Search for the fragrance
            params = {'query': query}
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                # This is a simplified example - real implementation would parse HTML
                # to find the first search result and extract the bottle image URL
                # For now, return None as we'd need BeautifulSoup for proper parsing
                pass

        except Exception as e:
            print(f"Error searching Fragrantica: {e}")

        return None

    def search_parfumo(self, cologne_name: str, brand: str) -> Optional[str]:
        """Search for cologne image on Parfumo (German fragrance site)"""
        try:
            # Similar implementation would go here
            # This would require parsing HTML to find bottle images
            pass

        except Exception as e:
            print(f"Error searching Parfumo: {e}")

        return None

    def download_placeholder_image(self) -> bytes:
        """Generate a simple placeholder image for colognes without photos"""
        try:
            if not self.dependencies_available or Image is None:
                return b''  # Return empty bytes if PIL not available

            # Create a simple placeholder image
            img = Image.new('RGB', (300, 400), color=(240, 240, 240))

            # You could add text or a simple bottle silhouette here
            output = BytesIO()
            img.save(output, format='JPEG', quality=80)
            return output.getvalue()

        except Exception:
            # Return minimal placeholder
            return b''

    def get_cologne_image(self, cologne_name: str, brand: str, force_refresh: bool = False) -> Tuple[bool, str]:
        """
        Get cologne bottle image, either from cache or by downloading

        Returns:
            Tuple[bool, str]: (success, file_path or error_message)
        """
        cache_key = self._generate_cache_key(cologne_name, brand)
        file_path = os.path.join(self.storage_path, f"{cache_key}.jpg")

        # Check if image already exists and not forcing refresh
        if not force_refresh and os.path.exists(file_path):
            return True, file_path

        # Try to find image online
        image_url = None

        # Try Fragrantica first
        image_url = self.search_fragrantica(cologne_name, brand)

        # If not found, try Parfumo
        if not image_url:
            image_url = self.search_parfumo(cologne_name, brand)

        # Download and save image
        if image_url:
            success, result = self._download_and_save_image(image_url, file_path, cologne_name, brand)
        else:
            # Use placeholder image
            success, result = self._save_placeholder_image(file_path, cologne_name, brand)

        return success, result

    def _download_and_save_image(self, image_url: str, file_path: str, cologne_name: str, brand: str) -> Tuple[bool, str]:
        """Download image from URL and save with compression"""
        if not self.dependencies_available or requests is None:
            return False, "Dependencies not available for image download"

        try:
            response = requests.get(image_url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Compress image
            compressed_data = self._compress_image(response.content)

            # Save to disk
            with open(file_path, 'wb') as f:
                f.write(compressed_data)

            # Update cache
            cache_key = self._generate_cache_key(cologne_name, brand)
            self.cache["images"][cache_key] = {
                "cologne_name": cologne_name,
                "brand": brand,
                "file_path": file_path,
                "downloaded_at": datetime.now().isoformat(),
                "size_kb": len(compressed_data) // 1024,
                "source": "online"
            }

            self._update_cache_stats()
            self._save_cache()

            return True, file_path

        except Exception as e:
            return False, f"Download failed: {str(e)}"

    def _save_placeholder_image(self, file_path: str, cologne_name: str, brand: str) -> Tuple[bool, str]:
        """Save placeholder image when no online image found"""
        try:
            placeholder_data = self.download_placeholder_image()

            with open(file_path, 'wb') as f:
                f.write(placeholder_data)

            # Update cache
            cache_key = self._generate_cache_key(cologne_name, brand)
            self.cache["images"][cache_key] = {
                "cologne_name": cologne_name,
                "brand": brand,
                "file_path": file_path,
                "downloaded_at": datetime.now().isoformat(),
                "size_kb": len(placeholder_data) // 1024,
                "source": "placeholder"
            }

            self._update_cache_stats()
            self._save_cache()

            return True, file_path

        except Exception as e:
            return False, f"Placeholder creation failed: {str(e)}"

    def _update_cache_stats(self):
        """Update cache statistics"""
        total_size_mb = self._get_storage_size()
        total_images = len(self.cache["images"])

        self.cache["stats"] = {
            "total_size_mb": round(total_size_mb, 2),
            "total_images": total_images,
            "last_updated": datetime.now().isoformat()
        }

    def get_storage_stats(self) -> Dict:
        """Get current storage statistics"""
        self._update_cache_stats()
        return self.cache["stats"]

    def is_storage_size_warning(self) -> bool:
        """Check if storage size exceeds warning threshold"""
        stats = self.get_storage_stats()
        return stats["total_size_mb"] > self.max_collection_size_mb

    def cleanup_old_images(self, days_old: int = 90):
        """Remove images older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        removed_count = 0
        to_remove = []

        for cache_key, image_info in self.cache["images"].items():
            try:
                download_date = datetime.fromisoformat(image_info["downloaded_at"]).timestamp()
                if download_date < cutoff_date:
                    # Remove file
                    if os.path.exists(image_info["file_path"]):
                        os.remove(image_info["file_path"])
                    to_remove.append(cache_key)
                    removed_count += 1
            except:
                continue

        # Remove from cache
        for cache_key in to_remove:
            del self.cache["images"][cache_key]

        self._update_cache_stats()
        self._save_cache()

        return removed_count

    def delete_cologne_image(self, cologne_name: str, brand: str) -> bool:
        """Delete specific cologne image"""
        cache_key = self._generate_cache_key(cologne_name, brand)

        if cache_key in self.cache["images"]:
            image_info = self.cache["images"][cache_key]

            # Remove file
            if os.path.exists(image_info["file_path"]):
                os.remove(image_info["file_path"])

            # Remove from cache
            del self.cache["images"][cache_key]

            self._update_cache_stats()
            self._save_cache()

            return True

        return False

    def get_collection_size_warning(self) -> Optional[str]:
        """Get warning message if collection is getting large"""
        stats = self.get_storage_stats()
        size_mb = stats["total_size_mb"]

        if size_mb > self.max_collection_size_mb * 1.5:
            return f"⚠️ Large collection: {size_mb:.1f}MB of images. Consider cleanup."
        elif size_mb > self.max_collection_size_mb:
            return f"💾 Collection growing: {size_mb:.1f}MB of images stored."

        return None


# Example usage and testing
if __name__ == "__main__":
    api = PhotoAPI()

    # Test getting an image
    success, result = api.get_cologne_image("Bleu de Chanel", "Chanel")
    print(f"Image fetch result: {success}, Path: {result}")

    # Get storage stats
    stats = api.get_storage_stats()
    print(f"Storage stats: {stats}")

    # Check for warnings
    warning = api.get_collection_size_warning()
    if warning:
        print(warning)