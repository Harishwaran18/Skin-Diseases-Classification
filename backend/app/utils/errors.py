"""Structured error handling — no stack traces / medical info in responses."""
from __future__ import annotations

from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base application error with a safe, user-facing message."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail, status_code=status.HTTP_404_NOT_FOUND)


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Not permitted") -> None:
        super().__init__(detail, status_code=status.HTTP_403_FORBIDDEN)


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Authentication required") -> None:
        super().__init__(detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ValidationError(AppError):
    def __init__(self, detail: str = "Invalid input") -> None:
        super().__init__(detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
