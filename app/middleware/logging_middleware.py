"""
Middleware для логирования HTTP запросов.
Автоматическое логирование всех входящих запросов и ответов.
"""

import time
import uuid
from typing import Any
from flask import Flask, request, g, Response, current_app
from loguru import logger
from app.utils import log_request, log_performance
from app.utils.logging import get_logger


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
        """
        Обработка запроса перед выполнением.
        Устанавливает request_id и логирует информацию о запросе.
        """
        # Генерируем уникальный ID для запроса
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        # Пропускаем логирование для статических файлов в production
        if self._is_static_request() and current_app.config.get('ENV') == 'production':
            return
            
        logger = get_logger('requests').bind(request_id=g.request_id)
        
        # Логируем основную информацию о запросе
        logger.info(
            "Incoming request",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent', 'Unknown')[:100]
        )
        
        # Логируем параметры запроса (кроме чувствительных)
        if request.args:
            sensitive_params = ['password', 'token', 'api_key', 'secret']
            safe_args = {k: '***' if any(s in k.lower() for s in sensitive_params) else v 
                        for k, v in request.args.items()}
            if safe_args:
                logger.debug("Query parameters", params=safe_args)
        
        # Логируем заголовки (кроме чувствительных)
        sensitive_headers = ['authorization', 'cookie', 'x-api-key', 'x-auth-token']
        safe_headers = {k: v for k, v in request.headers.items() 
                       if k.lower() not in sensitive_headers}
        logger.debug("Request headers", headers=safe_headers)
    
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
        request_id = getattr(g, 'request_id', None)
        
        # Получаем размер ответа
        response_size = len(response.get_data()) if hasattr(response, 'get_data') else None
        
        logger = get_logger('requests').bind(request_id=request_id)
        
        # Логируем ответ
        log_request(
            response_status=response.status_code,
            response_size=response_size,
            duration=duration
        )
        
        # Добавляем заголовок с ID запроса
        if request_id:
            response.headers['X-Request-ID'] = request_id
        
        # Логируем медленные запросы
        if duration > 1.0:
            log_performance(
                operation=f"{request.method} {request.path}",
                duration=duration,
                details={
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'response_size': response_size
                }
            )
        
        # Логируем подробности ответа
        logger.info(
            "Response completed",
            method=request.method,
            path=request.path,
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
        request_id = getattr(g, 'request_id', None)
        
        if error:
            logger = get_logger('errors').bind(request_id=request_id)
            logger.error(
                "Request error occurred",
                error_type=type(error).__name__,
                error_message=str(error),
                method=request.method,
                path=request.path
            )
    
    def _is_static_request(self) -> bool:
        """
        Проверка, является ли запрос статическим файлом.
        
        Returns:
            bool: True если это статический файл
        """
        static_prefixes = ['/static/', '/favicon.ico', '/robots.txt', '/sitemap.xml']
        return any(request.path.startswith(prefix) for prefix in static_prefixes) 