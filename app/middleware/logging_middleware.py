"""
Middleware для логирования HTTP запросов.
Автоматическое логирование всех входящих запросов и ответов.
"""

import time
import uuid
from typing import Any
from flask import Flask, request, g, Response
from loguru import logger
from app.utils import log_request, log_performance


class LoggingMiddleware:
    """Middleware для логирования HTTP запросов."""
    
    def __init__(self, app: Flask = None):
        """
        Инициализация middleware.
        
        Args:
            app: Flask приложение
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Инициализация middleware для приложения.
        
        Args:
            app: Flask приложение
        """
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)
    
    def _before_request(self) -> None:
        """Обработка запроса перед выполнением."""
        # Генерируем уникальный ID запроса
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Пропускаем статические файлы
        if self._is_static_request():
            return
        
        # Логируем начало запроса
        logger.info(
            f"REQUEST {request.method} {request.path} from {request.environ.get('REMOTE_ADDR')}",
            request_id=g.request_id,
            method=request.method,
            path=request.path,
            remote_addr=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent', '')[:200],
            content_type=request.content_type,
            content_length=request.content_length
        )
        
        # Логируем параметры запроса (кроме паролей)
        if request.args:
            safe_args = {k: v for k, v in request.args.items() 
                        if not any(sensitive in k.lower() for sensitive in ['password', 'token', 'secret', 'key'])}
            if safe_args:
                logger.debug(f"Query parameters: {safe_args}", request_id=g.request_id)
        
        # Логируем заголовки (кроме чувствительных)
        sensitive_headers = ['authorization', 'cookie', 'x-api-key', 'x-auth-token']
        safe_headers = {k: v for k, v in request.headers.items() 
                       if k.lower() not in sensitive_headers}
        logger.debug(f"Request headers: {safe_headers}", request_id=g.request_id)
    
    def _after_request(self, response: Response) -> Response:
        """
        Обработка ответа после выполнения.
        
        Args:
            response: HTTP ответ
            
        Returns:
            Response: Обработанный ответ
        """
        # Пропускаем статические файлы
        if self._is_static_request():
            return response
        
        # Вычисляем время выполнения
        duration = time.time() - getattr(g, 'start_time', time.time())
        
        # Получаем размер ответа
        response_size = len(response.get_data()) if hasattr(response, 'get_data') else None
        
        # Логируем ответ
        log_request(
            response_status=response.status_code,
            response_size=response_size,
            duration=duration
        )
        
        # Добавляем заголовок с ID запроса
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Логируем медленные запросы
        if duration > 1.0:
            log_performance(
                operation=f"{request.method} {request.path}",
                duration=duration,
                details={
                    'request_id': getattr(g, 'request_id', None),
                    'status_code': response.status_code,
                    'response_size': response_size
                }
            )
        
        # Логируем подробности ответа
        logger.info(
            f"RESPONSE {response.status_code} for {request.method} {request.path} ({duration:.3f}s)",
            request_id=getattr(g, 'request_id', None),
            status_code=response.status_code,
            duration=round(duration, 3),
            response_size=response_size,
            content_type=response.content_type
        )
        
        return response
    
    def _teardown_request(self, error: Any = None) -> None:
        """
        Очистка после запроса.
        
        Args:
            error: Ошибка, если произошла
        """
        if error:
            logger.error(
                f"Request error: {error}",
                request_id=getattr(g, 'request_id', None),
                error_type=type(error).__name__,
                exc_info=True
            )
    
    def _is_static_request(self) -> bool:
        """
        Проверка, является ли запрос статическим файлом.
        
        Returns:
            bool: True если это статический файл
        """
        static_prefixes = ['/static/', '/favicon.ico', '/robots.txt', '/sitemap.xml']
        return any(request.path.startswith(prefix) for prefix in static_prefixes) 