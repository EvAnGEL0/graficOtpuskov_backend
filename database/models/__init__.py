# database/models/__init__.py
from .user import User
from .todo import Todo

# Чтобы Alembic видел все модели
__all__ = ["User", "Todo"]