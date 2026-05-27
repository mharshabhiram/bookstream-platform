"""
Ebook processing service for metadata extraction and cover generation.
"""

import io
import json
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

import ebooklib
from ebooklib import epub
from PIL import Image
import fitz  # PyMuPDF

from src.core.config import settings
from src.core.logging import get_logger
from src.exceptions.base import EbookProcessingError
from src.services.storage import storage_service

logger = get_logger(__name__)


class EbookProcessor:
    """Process ebook files to extract metadata, covers, and TOC."""

    SUPPORTED_FORMATS = {".epub", ".pdf", ".mobi", ".azw3", ".txt"}

    async def process_book(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Process an ebook file and extract all metadata."""
        ext = Path(filename).suffix.lower()

        if ext not in self.SUPPORTED_FORMATS:
            raise EbookProcessingError(f"Unsupported format: {ext}")

        logger.info("processing_book", filename=filename, format=ext)

        try:
            if ext == ".epub":
                return await self._process_epub(file_data, filename, user_id)
            elif ext == ".pdf":
                return await self._process_pdf(file_data, filename, user_id)
            elif ext == ".txt":
                return await self._process_txt(file_data, filename, user_id)
            else:
                # MOBI/AZW3 - basic processing
                return await self._process_generic(file_data, filename, user_id)
        except Exception as e:
            logger.error("book_processing_failed", error=str(e), filename=filename)
            raise EbookProcessingError(f"Failed to process book: {str(e)}")

    async def _process_epub(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Process EPUB file."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name

        try:
            book = epub.read_epub(tmp_path)

            # Extract metadata
            metadata = {
                "title": self._get_epub_metadata(book, "title", filename),
                "author": self._get_epub_metadata(book, "creator", "Unknown Author"),
                "description": self._get_epub_metadata(book, "description", ""),
                "language": self._get_epub_metadata(book, "language", "en"),
                "publisher": self._get_epub_metadata(book, "publisher", ""),
                "isbn": self._get_epub_metadata(book, "identifier", ""),
                "published_date": self._get_epub_metadata(book, "date", ""),
            }

            # Extract cover
            cover_url = None
            cover_blurhash = None
            thumbnail_url = None

            cover_item = self._find_epub_cover(book)
            if cover_item:
                cover_data = cover_item.get_content()
                cover_url, thumbnail_url, cover_blurhash = await self._process_cover(
                    cover_data, user_id
                )

            # Extract TOC
            toc = self._extract_epub_toc(book)

            # Count pages (approximate from spine)
            page_count = len(book.spine)

            return {
                "title": metadata["title"],
                "author_name": metadata["author"],
                "description": metadata["description"],
                "language": metadata["language"],
                "publisher": metadata["publisher"],
                "isbn": metadata["isbn"],
                "published_date": metadata["published_date"],
                "page_count": page_count,
                "cover_url": cover_url,
                "cover_blurhash": cover_blurhash,
                "thumbnail_url": thumbnail_url,
                "toc": toc,
                "metadata": metadata,
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def _process_pdf(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Process PDF file."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name

        try:
            doc = fitz.open(tmp_path)

            # Extract metadata
            pdf_metadata = doc.metadata

            metadata = {
                "title": pdf_metadata.get("title", filename),
                "author": pdf_metadata.get("author", "Unknown Author"),
                "description": pdf_metadata.get("subject", ""),
                "language": "en",
                "publisher": pdf_metadata.get("producer", ""),
                "published_date": pdf_metadata.get("creationDate", ""),
            }

            # Extract cover from first page
            cover_url = None
            cover_blurhash = None
            thumbnail_url = None

            if doc.page_count > 0:
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                cover_data = pix.tobytes("png")
                cover_url, thumbnail_url, cover_blurhash = await self._process_cover(
                    cover_data, user_id
                )

            # Extract TOC
            toc = []
            try:
                pdf_toc = doc.get_toc()
                for level, title, page_num in pdf_toc:
                    toc.append({
                        "id": f"page-{page_num}",
                        "title": title,
                        "page": page_num,
                        "level": level,
                    })
            except Exception:
                pass

            page_count = doc.page_count
            doc.close()

            return {
                "title": metadata["title"],
                "author_name": metadata["author"],
                "description": metadata["description"],
                "language": metadata["language"],
                "publisher": metadata["publisher"],
                "isbn": "",
                "published_date": metadata["published_date"],
                "page_count": page_count,
                "cover_url": cover_url,
                "cover_blurhash": cover_blurhash,
                "thumbnail_url": thumbnail_url,
                "toc": toc,
                "metadata": metadata,
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def _process_txt(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Process TXT file."""
        try:
            text = file_data.decode("utf-8")
        except UnicodeDecodeError:
            text = file_data.decode("latin-1")

        # Simple title extraction from first line
        lines = text.strip().split("\n")
        title = lines[0][:200] if lines else filename

        # Word count
        word_count = len(text.split())
        page_count = word_count // 250  # Approximate

        return {
            "title": title,
            "author_name": "Unknown Author",
            "description": text[:500] if len(text) > 500 else text,
            "language": "en",
            "publisher": "",
            "isbn": "",
            "published_date": "",
            "page_count": max(page_count, 1),
            "cover_url": None,
            "cover_blurhash": None,
            "thumbnail_url": None,
            "toc": [],
            "metadata": {"word_count": word_count},
        }

    async def _process_generic(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Process generic ebook formats."""
        return {
            "title": Path(filename).stem,
            "author_name": "Unknown Author",
            "description": "",
            "language": "en",
            "publisher": "",
            "isbn": "",
            "published_date": "",
            "page_count": None,
            "cover_url": None,
            "cover_blurhash": None,
            "thumbnail_url": None,
            "toc": [],
            "metadata": {},
        }

    def _get_epub_metadata(self, book: epub.EpubBook, key: str, default: str) -> str:
        """Get EPUB metadata value."""
        values = book.get_metadata("DC", key)
        if values:
            return str(values[0][0])
        return default

    def _find_epub_cover(self, book: epub.EpubBook) -> epub.EpubItem | None:
        """Find cover image in EPUB."""
        # Try manifest cover
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                if "cover" in item.get_name().lower():
                    return item

        # Try first image
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                return item

        return None

    def _extract_epub_toc(self, book: epub.EpubBook) -> list[dict]:
        """Extract table of contents from EPUB."""
        toc = []

        def process_toc_item(item, level=0):
            if isinstance(item, tuple):
                label, href = item[0], item[1]
                toc.append({
                    "id": href.split("#")[-1] if "#" in href else href,
                    "title": label,
                    "href": href,
                    "level": level,
                })
                if len(item) > 2:
                    for child in item[2]:
                        process_toc_item(child, level + 1)
            elif isinstance(item, list):
                for child in item:
                    process_toc_item(child, level)

        for item in book.toc:
            process_toc_item(item)

        return toc

    async def _process_cover(
        self,
        image_data: bytes,
        user_id: str,
    ) -> tuple[str | None, str | None, str | None]:
        """Process and upload cover image with thumbnail."""
        try:
            # Validate image
            img = Image.open(io.BytesIO(image_data))
            img.verify()

            # Upload original cover
            cover_key = storage_service.generate_key("covers", "cover.webp", user_id)
            cover_url = await storage_service.upload_file(
                image_data, cover_key, "image/webp"
            )

            # Generate and upload thumbnail
            thumb_data = await storage_service.generate_thumbnail(
                image_data, width=300, height=450
            )
            thumb_key = storage_service.generate_key("covers", "thumb.webp", user_id)
            thumbnail_url = await storage_service.upload_file(
                thumb_data, thumb_key, "image/webp"
            )

            # Generate blurhash (simplified - in production use blurhash library)
            cover_blurhash = None

            return cover_url, thumbnail_url, cover_blurhash
        except Exception as e:
            logger.warning("cover_processing_failed", error=str(e))
            return None, None, None


# Singleton
ebook_processor = EbookProcessor()
