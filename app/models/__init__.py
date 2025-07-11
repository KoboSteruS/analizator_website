"""
Модели базы данных.
Содержит BaseModel и импорты всех моделей.
"""

from .base import BaseModel
from .user import User
from .service import Service
from .portfolio import Portfolio

# Здесь будут импорты всех моделей при их создании
# from .loan import Loan

__all__ = [
    'BaseModel',
    'User',
    'Service',
    'Portfolio',
    # Добавлять новые модели в этот список
] 