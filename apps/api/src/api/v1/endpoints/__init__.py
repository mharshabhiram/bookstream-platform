"""
API v1 router assembly.
"""

from fastapi import APIRouter

from src.api.v1.endpoints import auth, books, reading, users

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(books.router)
router.include_router(reading.router)
router.include_router(users.router)
