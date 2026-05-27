"""
Book API endpoints.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logging import get_logger
from src.db.session import get_db_session
from src.crud.book import book_crud, user_book_crud, category_crud
from src.services.auth import get_current_active_user
from src.services.storage import storage_service
from src.services.ebook import ebook_processor
from src.models.user import User
from src.models.book import Book
from src.schemas.book import (
    BookResponse,
    BookDetailResponse,
    BookListResponse,
    BookUploadResponse,
    BookSearchFilters,
    UserBookUpdate,
    UserBookResponse,
)
from src.schemas.common import MessageResponse, PaginatedResponse
from src.exceptions.base import NotFoundException, BadRequestException

logger = get_logger(__name__)
router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=PaginatedResponse[BookResponse])
async def list_books(
    filters: BookSearchFilters = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """List books with search and filters."""
    books, total = await book_crud.search(db, filters)

    pages = (total + filters.page_size - 1) // filters.page_size

    return {
        "items": [BookResponse.model_validate(b) for b in books],
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size,
        "pages": pages,
        "has_next": filters.page < pages,
        "has_prev": filters.page > 1,
    }


@router.get("/featured", response_model=list[BookResponse])
async def get_featured_books(
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
) -> list[BookResponse]:
    """Get featured books."""
    books = await book_crud.get_featured(db, limit=limit)
    return [BookResponse.model_validate(b) for b in books]


@router.get("/trending", response_model=list[BookResponse])
async def get_trending_books(
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
) -> list[BookResponse]:
    """Get trending books."""
    books = await book_crud.get_trending(db, limit=limit)
    return [BookResponse.model_validate(b) for b in books]


@router.get("/recent", response_model=list[BookResponse])
async def get_recent_books(
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
) -> list[BookResponse]:
    """Get recently added books."""
    books = await book_crud.get_recent(db, limit=limit)
    return [BookResponse.model_validate(b) for b in books]


@router.get("/categories", response_model=list)
async def get_categories(
    db: AsyncSession = Depends(get_db_session),
) -> list:
    """Get all book categories."""
    categories = await category_crud.get_multi(db, limit=100)
    return [{"id": str(c.id), "name": c.name, "slug": c.slug} for c in categories]


@router.get("/{book_id}", response_model=BookDetailResponse)
async def get_book(
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User | None = Depends(get_current_active_user),
) -> BookDetailResponse:
    """Get book details."""
    book = await book_crud.get_with_relations(db, book_id)
    if not book:
        raise NotFoundException("Book", str(book_id))

    # Check if user has this book in library
    user_book = None
    if current_user:
        ub = await user_book_crud.get_by_user_book(db, current_user.id, book_id)
        if ub:
            user_book = UserBookResponse.model_validate(ub)

    response = BookDetailResponse.model_validate(book)
    response.user_book = user_book
    return response


@router.post("/upload", response_model=BookUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_book(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> BookUploadResponse:
    """Upload a new ebook."""
    # Validate file
    if not file.filename:
        raise BadRequestException("No file provided")

    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise BadRequestException(f"Unsupported file format: {ext}")

    # Read file
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException("File too large")

    # Compute hash
    file_hash = storage_service.compute_hash(contents)

    # Check for duplicates
    from sqlalchemy import select
    from src.models.book import Book as BookModel
    existing = await db.execute(
        select(BookModel).where(BookModel.file_hash == file_hash)
    )
    if existing.scalar_one_or_none():
        raise BadRequestException("This book has already been uploaded")

    # Upload file to storage
    file_key = storage_service.generate_key("books", file.filename, str(current_user.id))
    file_url = await storage_service.upload_file(
        contents,
        file_key,
        content_type=file.content_type or "application/octet-stream",
    )

    # Process ebook metadata
    try:
        metadata = await ebook_processor.process_book(
            contents,
            file.filename,
            str(current_user.id),
        )
    except Exception as e:
        logger.error("book_processing_failed", error=str(e))
        metadata = {
            "title": title or file.filename,
            "author_name": "Unknown",
            "description": "",
            "language": "en",
            "page_count": None,
            "cover_url": None,
            "thumbnail_url": None,
            "toc": [],
            "metadata": {},
        }

    # Create book record
    from slugify import slugify
    book_data = {
        "title": metadata.get("title", title or file.filename),
        "slug": slugify(metadata.get("title", file.filename)) + "-" + str(uuid4())[:8],
        "author_name": metadata.get("author_name"),
        "description": metadata.get("description"),
        "language": metadata.get("language", "en"),
        "page_count": metadata.get("page_count"),
        "file_url": file_url,
        "file_size": len(contents),
        "file_format": ext[1:],  # Remove dot
        "file_hash": file_hash,
        "cover_url": metadata.get("cover_url"),
        "cover_blurhash": metadata.get("cover_blurhash"),
        "thumbnail_url": metadata.get("thumbnail_url"),
        "toc": metadata.get("toc"),
        "metadata": metadata.get("metadata"),
        "uploaded_by_id": current_user.id,
        "is_processed": True,
    }

    book = await book_crud.create(db, obj_in=book_data)

    # Add to user's library
    await user_book_crud.create(db, obj_in={
        "user_id": current_user.id,
        "book_id": book.id,
        "status": "unread",
    })

    logger.info("book_uploaded", book_id=str(book.id), user_id=str(current_user.id))

    return BookUploadResponse(
        id=book.id,
        title=book.title,
        status="completed",
    )


@router.post("/{book_id}/library", response_model=UserBookResponse)
async def add_to_library(
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserBookResponse:
    """Add book to user's library."""
    # Check if already in library
    existing = await user_book_crud.get_by_user_book(db, current_user.id, book_id)
    if existing:
        return UserBookResponse.model_validate(existing)

    user_book = await user_book_crud.create(db, obj_in={
        "user_id": current_user.id,
        "book_id": book_id,
        "status": "unread",
    })

    return UserBookResponse.model_validate(user_book)


@router.patch("/{book_id}/library", response_model=UserBookResponse)
async def update_library_book(
    book_id: UUID,
    data: UserBookUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserBookResponse:
    """Update user's library entry for a book."""
    user_book = await user_book_crud.get_by_user_book(db, current_user.id, book_id)
    if not user_book:
        raise NotFoundException("Library entry")

    update_data = data.model_dump(exclude_unset=True)
    updated = await user_book_crud.update(db, db_obj=user_book, obj_in=update_data)

    return UserBookResponse.model_validate(updated)


@router.delete("/{book_id}/library", response_model=MessageResponse)
async def remove_from_library(
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Remove book from user's library."""
    user_book = await user_book_crud.get_by_user_book(db, current_user.id, book_id)
    if user_book:
        await db.delete(user_book)
        await db.flush()

    return MessageResponse(message="Book removed from library")
