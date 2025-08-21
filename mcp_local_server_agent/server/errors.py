# server/errors.py
from __future__ import annotations


class UserInputError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class DatabaseError(Exception):
    pass
