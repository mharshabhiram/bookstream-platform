"""
File storage service supporting local, S3, and R2 backends.
"""

import hashlib
import io
import os
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

import aiofiles
from PIL import Image

from src.core.config import settings
from src.core.logging import get_logger
from src.exceptions.base import StorageError

logger = get_logger(__name__)


class StorageService:
    """File storage service with multiple backend support."""

    def __init__(self):
        self.backend = settings.STORAGE_TYPE
        self.bucket = settings.STORAGE_BUCKET
        self.initialized = False
        self._s3_client = None

    async def initialize(self) -> None:
        """Initialize storage backend."""
        if self.backend in ("s3", "r2"):
            import aiobotocore.session
            session = aiobotocore.session.get_session()
            self._s3_client = session.create_client(
                "s3",
                region_name=settings.STORAGE_REGION,
                endpoint_url=settings.STORAGE_ENDPOINT,
                aws_access_key_id=settings.STORAGE_ACCESS_KEY,
                aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            )
        elif self.backend == "local":
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            (upload_dir / "books").mkdir(exist_ok=True)
            (upload_dir / "covers").mkdir(exist_ok=True)
            (upload_dir / "avatars").mkdir(exist_ok=True)

        self.initialized = True
        logger.info("storage_initialized", backend=self.backend)

    def _get_local_path(self, key: str) -> Path:
        """Get local file path."""
        return Path("uploads") / key

    def _get_public_url(self, key: str) -> str:
        """Get public URL for a file."""
        if self.backend == "local":
            return f"{settings.API_URL}/uploads/{key}"
        elif settings.STORAGE_PUBLIC_URL:
            return f"{settings.STORAGE_PUBLIC_URL}/{key}"
        return f"https://{self.bucket}.s3.{settings.STORAGE_REGION}.amazonaws.com/{key}"

    async def upload_file(
        self,
        file_data: bytes | BinaryIO,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file to storage."""
        if isinstance(file_data, bytes):
            data = file_data
        else:
            data = file_data.read()

        if self.backend in ("s3", "r2"):
            async with self._s3_client as client:
                await client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=data,
                    ContentType=content_type,
                )
        else:
            path = self._get_local_path(key)
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, "wb") as f:
                await f.write(data)

        return self._get_public_url(key)

    async def delete_file(self, key: str) -> None:
        """Delete a file from storage."""
        try:
            if self.backend in ("s3", "r2"):
                async with self._s3_client as client:
                    await client.delete_object(Bucket=self.bucket, Key=key)
            else:
                path = self._get_local_path(key)
                if path.exists():
                    path.unlink()
        except Exception as e:
            logger.warning("file_delete_failed", key=key, error=str(e))

    async def generate_thumbnail(
        self,
        image_data: bytes,
        width: int = 300,
        height: int = 450,
        quality: int = 85,
    ) -> bytes:
        """Generate a thumbnail from image data."""
        try:
            img = Image.open(io.BytesIO(image_data))
            img = img.convert("RGB")

            # Calculate crop for book cover aspect ratio (2:3)
            target_ratio = width / height
            current_ratio = img.width / img.height

            if current_ratio > target_ratio:
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            else:
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))

            img = img.resize((width, height), Image.LANCZOS)

            output = io.BytesIO()
            img.save(output, format="WEBP", quality=quality, method=6)
            return output.getvalue()
        except Exception as e:
            logger.error("thumbnail_generation_failed", error=str(e))
            raise StorageError("Failed to generate thumbnail")

    def generate_key(
        self,
        prefix: str,
        filename: str,
        user_id: str | None = None,
    ) -> str:
        """Generate a unique storage key."""
        ext = Path(filename).suffix.lower()
        unique_id = str(uuid4())
        if user_id:
            return f"{prefix}/{user_id}/{unique_id}{ext}"
        return f"{prefix}/{unique_id}{ext}"

    def compute_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash of file data."""
        return hashlib.sha256(data).hexdigest()


# Singleton
storage_service = StorageService()
