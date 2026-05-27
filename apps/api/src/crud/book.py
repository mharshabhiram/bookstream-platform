"""
Book CRUD operations.
"""

from uuid import UUID

from sqlalchemy import select, func, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.logging import get_logger
from src.crud.base import BaseCRUD
from src.models.book import Author, Category, Book, BookCategory, UserBook
from src.schemas.book import BookCreate, BookSearchFilters

logger = get_logger(__name__)


class AuthorCRUD(BaseCRUD[Author]):
    """Author CRUD operations."""

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Author | None:
        result = await db.execute(
            select(Author).where(Author.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        db: AsyncSession,
        *,
        name: str,
        **kwargs,
    ) -> Author:
        result = await db.execute(
            select(Author).where(Author.name.ilike(name))
        )
        author = result.scalar_one_or_none()
        if author:
            return author

        from slugify import slugify
        author = Author(
            name=name,
            slug=slugify(name),
            **kwargs,
        )
        db.add(author)
        await db.flush()
        await db.refresh(author)
        return author


class CategoryCRUD(BaseCRUD[Category]):
    """Category CRUD operations."""

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Category | None:
        result = await db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_featured(self, db: AsyncSession) -> list[Category]:
        result = await db.execute(
            select(Category)
            .where(Category.is_featured == True)
            .order_by(Category.sort_order)
        )
        return list(result.scalars().all())


class BookCRUD(BaseCRUD[Book]):
    """Book CRUD operations."""

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Book | None:
        result = await db.execute(
            select(Book)
            .where(Book.slug == slug)
            .options(
                selectinload(Book.author),
                selectinload(Book.categories).selectinload(BookCategory.category),
            )
        )
        return result.scalar_one_or_none()

    async def get_with_relations(self, db: AsyncSession, book_id: UUID) -> Book | None:
        result = await db.execute(
            select(Book)
            .where(Book.id == book_id)
            .options(
                selectinload(Book.author),
                selectinload(Book.categories).selectinload(BookCategory.category),
            )
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        db: AsyncSession,
        filters: BookSearchFilters,
    ) -> tuple[list[Book], int]:
        """Search books with filters."""
        query = select(Book).where(Book.is_public == True)

        if filters.query:
            search_term = f"%{filters.query}%"
            query = query.where(
                (Book.title.ilike(search_term)) |
                (Book.author_name.ilike(search_term)) |
                (Book.description.ilike(search_term))
            )

        if filters.category_id:
            query = query.join(BookCategory).where(
                BookCategory.category_id == filters.category_id
            )

        if filters.author_id:
            query = query.where(Book.author_id == filters.author_id)

        if filters.format:
            query = query.where(Book.file_format == filters.format)

        if filters.language:
            query = query.where(Book.language == filters.language)

        if filters.min_rating:
            query = query.where(Book.average_rating >= filters.min_rating)

        if filters.year_from:
            query = query.where(
                func.extract("year", Book.published_date) >= filters.year_from
            )

        if filters.year_to:
            query = query.where(
                func.extract("year", Book.published_date) <= filters.year_to
            )

        # Sorting
        sort_column = getattr(Book, filters.sort_by, Book.created_at)
        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Count total
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        result = await db.execute(query.options(
            selectinload(Book.author),
            selectinload(Book.categories).selectinload(BookCategory.category),
        ))

        return list(result.scalars().all()), total

    async def get_featured(self, db: AsyncSession, limit: int = 10) -> list[Book]:
        result = await db.execute(
            select(Book)
            .where(Book.is_featured == True)
            .where(Book.is_public == True)
            .order_by(desc(Book.average_rating))
            .limit(limit)
            .options(
                selectinload(Book.author),
                selectinload(Book.categories).selectinload(BookCategory.category),
            )
        )
        return list(result.scalars().all())

    async def get_trending(self, db: AsyncSession, limit: int = 10) -> list[Book]:
        result = await db.execute(
            select(Book)
            .where(Book.is_public == True)
            .order_by(desc(Book.total_reads))
            .limit(limit)
            .options(
                selectinload(Book.author),
                selectinload(Book.categories).selectinload(BookCategory.category),
            )
        )
        return list(result.scalars().all())

    async def get_recent(self, db: AsyncSession, limit: int = 10) -> list[Book]:
        result = await db.execute(
            select(Book)
            .where(Book.is_public == True)
            .order_by(desc(Book.created_at))
            .limit(limit)
            .options(
                selectinload(Book.author),
                selectinload(Book.categories).selectinload(BookCategory.category),
            )
        )
        return list(result.scalars().all())

    async def increment_reads(self, db: AsyncSession, book_id: UUID) -> None:
        await db.execute(
            update(Book)
            .where(Book.id == book_id)
            .values(total_reads=Book.total_reads + 1)
        )
        await db.flush()


class UserBookCRUD(BaseCRUD[UserBook]):
    """User book library CRUD."""

    async def get_by_user_book(
        self,
        db: AsyncSession,
        user_id: UUID,
        book_id: UUID,
    ) -> UserBook | None:
        result = await db.execute(
            select(UserBook)
            .where(UserBook.user_id == user_id)
            .where(UserBook.book_id == book_id)
            .options(selectinload(UserBook.book))
        )
        return result.scalar_one_or_none()

    async def get_user_library(
        self,
        db: AsyncSession,
        user_id: UUID,
        status: str | None = None,
        is_favorite: bool | None = None,
        is_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[UserBook], int]:
        query = select(UserBook).where(UserBook.user_id == user_id)

        if status:
            query = query.where(UserBook.status == status)
        if is_favorite is not None:
            query = query.where(UserBook.is_favorite == is_favorite)
        query = query.where(UserBook.is_archived == is_archived)

        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        query = query.order_by(desc(UserBook.last_read_at))
        query = query.offset(offset).limit(limit)

        result = await db.execute(
            query.options(selectinload(UserBook.book))
        )
        return list(result.scalars().all()), total

    async def get_continue_reading(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 5,
    ) -> list[UserBook]:
        result = await db.execute(
            select(UserBook)
            .where(UserBook.user_id == user_id)
            .where(UserBook.status == "reading")
            .where(UserBook.last_read_at.isnot(None))
            .order_by(desc(UserBook.last_read_at))
            .limit(limit)
            .options(selectinload(UserBook.book))
        )
        return list(result.scalars().all())


# Singleton instances
author_crud = AuthorCRUD(Author)
category_crud = CategoryCRUD(Category)
book_crud = BookCRUD(Book)
user_book_crud = UserBookCRUD(UserBook)
