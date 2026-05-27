"""
Reading progress, highlights, bookmarks, and notes endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.db.session import get_db_session
from src.crud.base import BaseCRUD
from src.services.auth import get_current_active_user
from src.models.user import User
from src.models.reading import ReadingProgress, Highlight, Bookmark, Note
from src.schemas.reading import (
    ReadingProgressUpdate,
    ReadingProgressResponse,
    HighlightCreate,
    HighlightUpdate,
    HighlightResponse,
    BookmarkCreate,
    BookmarkUpdate,
    BookmarkResponse,
    NoteCreate,
    NoteUpdate,
    NoteResponse,
)
from src.schemas.common import MessageResponse, PaginatedResponse
from src.exceptions.base import NotFoundException

logger = get_logger(__name__)
router = APIRouter(prefix="/reading", tags=["Reading"])

# CRUD instances
reading_progress_crud = BaseCRUD(ReadingProgress)
highlight_crud = BaseCRUD(Highlight)
bookmark_crud = BaseCRUD(Bookmark)
note_crud = BaseCRUD(Note)


# ─── Reading Progress ─────────────────────────────────────────────

@router.get("/progress/{book_id}", response_model=ReadingProgressResponse)
async def get_progress(
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ReadingProgressResponse:
    """Get reading progress for a book."""
    from sqlalchemy import select
    result = await db.execute(
        select(ReadingProgress)
        .where(ReadingProgress.user_id == current_user.id)
        .where(ReadingProgress.book_id == book_id)
    )
    progress = result.scalar_one_or_none()

    if not progress:
        # Return empty progress
        return ReadingProgressResponse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            book_id=book_id,
            progress_percent=0.0,
            time_spent_seconds=0,
            sessions_count=0,
            last_read_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )

    return ReadingProgressResponse.model_validate(progress)


@router.put("/progress/{book_id}", response_model=ReadingProgressResponse)
async def update_progress(
    book_id: UUID,
    data: ReadingProgressUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ReadingProgressResponse:
    """Update reading progress for a book."""
    from sqlalchemy import select
    result = await db.execute(
        select(ReadingProgress)
        .where(ReadingProgress.user_id == current_user.id)
        .where(ReadingProgress.book_id == book_id)
    )
    progress = result.scalar_one_or_none()

    update_data = data.model_dump(exclude_unset=True)

    if progress:
        # Update existing
        progress = await reading_progress_crud.update(
            db, db_obj=progress, obj_in=update_data
        )
        progress.sessions_count += 1
    else:
        # Create new
        update_data["user_id"] = current_user.id
        update_data["book_id"] = book_id
        update_data["started_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        update_data["sessions_count"] = 1
        progress = await reading_progress_crud.create(db, obj_in=update_data)

    # Update user_book last position
    from src.crud.book import user_book_crud
    user_book = await user_book_crud.get_by_user_book(db, current_user.id, book_id)
    if user_book:
        user_book.last_position = data.current_cfi or data.current_page
        user_book.last_progress_percent = data.progress_percent
        user_book.last_read_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        if data.progress_percent >= 99:
            user_book.status = "completed"
        elif data.progress_percent > 0:
            user_book.status = "reading"
        db.add(user_book)
        await db.flush()

    return ReadingProgressResponse.model_validate(progress)


# ─── Highlights ───────────────────────────────────────────────────

@router.get("/highlights/{book_id}", response_model=list[HighlightResponse])
async def get_highlights(
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> list[HighlightResponse]:
    """Get highlights for a book."""
    from sqlalchemy import select
    result = await db.execute(
        select(Highlight)
        .where(Highlight.user_id == current_user.id)
        .where(Highlight.book_id == book_id)
        .order_by(Highlight.created_at.desc())
    )
    highlights = result.scalars().all()
    return [HighlightResponse.model_validate(h) for h in highlights]


@router.post("/highlights", response_model=HighlightResponse, status_code=status.HTTP_201_CREATED)
async def create_highlight(
    data: HighlightCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> HighlightResponse:
    """Create a new highlight."""
    highlight_data = data.model_dump()
    highlight_data["user_id"] = current_user.id

    highlight = await highlight_crud.create(db, obj_in=highlight_data)
    return HighlightResponse.model_validate(highlight)


@router.patch("/highlights/{highlight_id}", response_model=HighlightResponse)
async def update_highlight(
    highlight_id: UUID,
    data: HighlightUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> HighlightResponse:
    """Update a highlight."""
    highlight = await highlight_crud.get(db, highlight_id)
    if not highlight or highlight.user_id != current_user.id:
        raise NotFoundException("Highlight")

    update_data = data.model_dump(exclude_unset=True)
    updated = await highlight_crud.update(db, db_obj=highlight, obj_in=update_data)
    return HighlightResponse.model_validate(updated)


@router.delete("/highlights/{highlight_id}", response_model=MessageResponse)
async def delete_highlight(
    highlight_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Delete a highlight."""
    highlight = await highlight_crud.get(db, highlight_id)
    if not highlight or highlight.user_id != current_user.id:
        raise NotFoundException("Highlight")

    await highlight_crud.delete(db, id=highlight_id)
    return MessageResponse(message="Highlight deleted")


# ─── Bookmarks ────────────────────────────────────────────────────

@router.get("/bookmarks/{book_id}", response_model=list[BookmarkResponse])
async def get_bookmarks(
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> list[BookmarkResponse]:
    """Get bookmarks for a book."""
    from sqlalchemy import select
    result = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == current_user.id)
        .where(Bookmark.book_id == book_id)
        .order_by(Bookmark.created_at.desc())
    )
    bookmarks = result.scalars().all()
    return [BookmarkResponse.model_validate(b) for b in bookmarks]


@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    data: BookmarkCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkResponse:
    """Create a new bookmark."""
    bookmark_data = data.model_dump()
    bookmark_data["user_id"] = current_user.id

    bookmark = await bookmark_crud.create(db, obj_in=bookmark_data)
    return BookmarkResponse.model_validate(bookmark)


@router.patch("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: UUID,
    data: BookmarkUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkResponse:
    """Update a bookmark."""
    bookmark = await bookmark_crud.get(db, bookmark_id)
    if not bookmark or bookmark.user_id != current_user.id:
        raise NotFoundException("Bookmark")

    update_data = data.model_dump(exclude_unset=True)
    updated = await bookmark_crud.update(db, db_obj=bookmark, obj_in=update_data)
    return BookmarkResponse.model_validate(updated)


@router.delete("/bookmarks/{bookmark_id}", response_model=MessageResponse)
async def delete_bookmark(
    bookmark_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Delete a bookmark."""
    bookmark = await bookmark_crud.get(db, bookmark_id)
    if not bookmark or bookmark.user_id != current_user.id:
        raise NotFoundException("Bookmark")

    await bookmark_crud.delete(db, id=bookmark_id)
    return MessageResponse(message="Bookmark deleted")


# ─── Notes ────────────────────────────────────────────────────────

@router.get("/notes/{book_id}", response_model=list[NoteResponse])
async def get_notes(
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> list[NoteResponse]:
    """Get notes for a book."""
    from sqlalchemy import select
    result = await db.execute(
        select(Note)
        .where(Note.user_id == current_user.id)
        .where(Note.book_id == book_id)
        .order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()
    return [NoteResponse.model_validate(n) for n in notes]


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: NoteCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> NoteResponse:
    """Create a new note."""
    note_data = data.model_dump()
    note_data["user_id"] = current_user.id

    note = await note_crud.create(db, obj_in=note_data)
    return NoteResponse.model_validate(note)


@router.patch("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    data: NoteUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> NoteResponse:
    """Update a note."""
    note = await note_crud.get(db, note_id)
    if not note or note.user_id != current_user.id:
        raise NotFoundException("Note")

    update_data = data.model_dump(exclude_unset=True)
    updated = await note_crud.update(db, db_obj=note, obj_in=update_data)
    return NoteResponse.model_validate(updated)


@router.delete("/notes/{note_id}", response_model=MessageResponse)
async def delete_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Delete a note."""
    note = await note_crud.get(db, note_id)
    if not note or note.user_id != current_user.id:
        raise NotFoundException("Note")

    await note_crud.delete(db, id=note_id)
    return MessageResponse(message="Note deleted")
