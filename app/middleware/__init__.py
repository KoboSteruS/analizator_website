"""
Middleware приложения.
Содержит промежуточное ПО для обработки запросов.
"""

from .logging_middleware import LoggingMiddleware

__all__ = ['LoggingMiddleware'] 