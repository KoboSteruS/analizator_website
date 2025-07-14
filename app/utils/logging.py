"""
Система логирования приложения.
Настройка структурированного логирования с loguru.
"""

import os
import sys
import logging
from typing import Dict, Any
from loguru import logger
from flask import Flask, request, g, has_request_context
from datetime import datetime
import json


class LoggerConfig:
    """Конфигурация логирования."""
    
    # Базовая директория для логов
    LOG_DIR = "logs"
    
    # Форматы логирования
    DETAILED_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    SIMPLE_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )
    
    JSON_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"
    )
    
    # Размеры ротации логов
    DEFAULT_ROTATION = "10 MB"
    LARGE_ROTATION = "50 MB"
    
    # Время хранения логов
    RETENTION = "30 days"
    
    # Уровни логирования для разных окружений
    LEVELS = {
        'development': 'DEBUG',
        'testing': 'INFO', 
        'production': 'WARNING'
    }


def create_log_directory():
    """Создание директории для логов."""
    if not os.path.exists(LoggerConfig.LOG_DIR):
        os.makedirs(LoggerConfig.LOG_DIR)


def get_request_context() -> Dict[str, Any]:
    """Получение контекста текущего запроса."""
    context = {}
    
    if has_request_context():
        context.update({
            'method': request.method,
            'url': request.url,
            'path': request.path,
            'remote_addr': request.environ.get('REMOTE_ADDR'),
            'user_agent': request.headers.get('User-Agent', ''),
            'content_type': request.content_type,
        })
        
        # Добавляем user_id если есть в сессии
        if hasattr(g, 'user_id'):
            context['user_id'] = g.user_id
            
        # Добавляем request_id если есть
        if hasattr(g, 'request_id'):
            context['request_id'] = g.request_id
    
    return context


def format_log_record(record):
    """Форматирование записи лога с дополнительным контекстом."""
    # Добавляем контекст запроса
    request_context = get_request_context()
    if request_context:
        record["extra"]["request"] = request_context
    
    return record


class LogInterceptHandler(logging.Handler):
    """Перехватчик стандартных Python логов для loguru."""
    
    def emit(self, record):
        # Получаем соответствующий уровень loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Находим caller frame
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(app: Flask) -> None:
    """
    Настройка комплексной системы логирования.
    
    Args:
        app: Flask приложение
    """
    create_log_directory()
    
    # Получаем конфигурацию логирования
    from app.config.logging import get_logging_config
    config_name = os.getenv('FLASK_ENV', 'development')
    logging_config = get_logging_config(config_name)
    log_level = logging_config.DEFAULT_LEVEL
    
    # Очищаем существующие handlers
    logger.remove()
    
    # === КОНСОЛЬНЫЙ ВЫВОД ===
    if logging_config.CONSOLE['enabled']:
        console_format = (LoggerConfig.DETAILED_FORMAT 
                         if logging_config.CONSOLE['format'] == 'detailed' 
                         else LoggerConfig.SIMPLE_FORMAT)
        
        logger.add(
            sys.stderr,
            format=console_format,
            level=logging_config.CONSOLE['level'],
            colorize=logging_config.CONSOLE['colorize'],
            backtrace=logging_config.BACKTRACE,
            diagnose=logging_config.DIAGNOSE,
            enqueue=logging_config.ENQUEUE
        )
    
    # === ОСНОВНОЙ ЛОГ ПРИЛОЖЕНИЯ ===
    logger.add(
        os.path.join(LoggerConfig.LOG_DIR, "app.log"),
        format=LoggerConfig.JSON_FORMAT,
        level=log_level,
        rotation=LoggerConfig.DEFAULT_ROTATION,
        retention=LoggerConfig.RETENTION,
        compression="gz",
        backtrace=True,
        diagnose=True,
        serialize=False
    )
    
    # === ОШИБКИ И ИСКЛЮЧЕНИЯ ===
    logger.add(
        os.path.join(LoggerConfig.LOG_DIR, "errors.log"),
        format=LoggerConfig.JSON_FORMAT,
        level="ERROR",
        rotation=LoggerConfig.DEFAULT_ROTATION,
        retention=LoggerConfig.RETENTION,
        compression="gz",
        backtrace=True,
        diagnose=True,
        filter=lambda record: record["level"].name in ["ERROR", "CRITICAL"]
    )
    
    # === HTTP ЗАПРОСЫ ===
    logger.add(
        os.path.join(LoggerConfig.LOG_DIR, "requests.log"),
        format=LoggerConfig.JSON_FORMAT,
        level="INFO",
        rotation=LoggerConfig.LARGE_ROTATION,
        retention=LoggerConfig.RETENTION,
        compression="gz",
        filter=lambda record: "REQUEST" in record["message"] or "RESPONSE" in record["message"]
    )
    
    # === БЕЗОПАСНОСТЬ ===
    logger.add(
        os.path.join(LoggerConfig.LOG_DIR, "security.log"),
        format=LoggerConfig.JSON_FORMAT,
        level="WARNING",
        rotation=LoggerConfig.DEFAULT_ROTATION,
        retention="90 days",  # Дольше храним логи безопасности
        compression="gz",
        filter=lambda record: any(keyword in record["message"].upper() for keyword in 
                                ["AUTH", "LOGIN", "LOGOUT", "SECURITY", "ADMIN", "JWT", "UNAUTHORIZED", "FORBIDDEN"])
    )
    
    # === АДМИНКА ===
    logger.add(
        os.path.join(LoggerConfig.LOG_DIR, "admin.log"),
        format=LoggerConfig.JSON_FORMAT,
        level="INFO",
        rotation=LoggerConfig.DEFAULT_ROTATION,
        retention=LoggerConfig.RETENTION,
        compression="gz",
        filter=lambda record: "admin" in record["name"] or "ADMIN" in record["message"]
    )
    
    # === БАЗА ДАННЫХ ===
    if app.config.get('SQLALCHEMY_ECHO') or app.config.get('DEBUG'):
        logger.add(
            os.path.join(LoggerConfig.LOG_DIR, "database.log"),
            format=LoggerConfig.JSON_FORMAT,
            level="DEBUG",
            rotation=LoggerConfig.LARGE_ROTATION,
            retention="7 days",  # БД логи быстро накапливаются
            compression="gz",
            filter=lambda record: any(keyword in record["name"] for keyword in 
                                    ["sqlalchemy", "database", "db"])
        )
    
    # === ФАЙЛОВЫЕ ОПЕРАЦИИ ===
    logger.add(
        os.path.join(LoggerConfig.LOG_DIR, "files.log"),
        format=LoggerConfig.JSON_FORMAT,
        level="INFO",
        rotation=LoggerConfig.DEFAULT_ROTATION,
        retention=LoggerConfig.RETENTION,
        compression="gz",
        filter=lambda record: any(keyword in record["message"].upper() for keyword in 
                                ["UPLOAD", "DOWNLOAD", "FILE", "IMAGE", "DELETE"])
    )
    
    # === ПРОИЗВОДИТЕЛЬНОСТЬ ===
    logger.add(
        os.path.join(LoggerConfig.LOG_DIR, "performance.log"),
        format=LoggerConfig.JSON_FORMAT,
        level="INFO",
        rotation=LoggerConfig.DEFAULT_ROTATION,
        retention="14 days",
        compression="gz",
        filter=lambda record: any(keyword in record["message"].upper() for keyword in 
                                ["SLOW", "PERFORMANCE", "TIME", "DURATION", "LATENCY"])
    )
    
    # Перехватываем стандартные Python логи
    intercept_handler = LogInterceptHandler()
    
    # Настраиваем перехват для основных логгеров
    loggers_to_intercept = [
        "werkzeug",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
        "alembic"
    ]
    
    for logger_name in loggers_to_intercept:
        logging.getLogger(logger_name).handlers = [intercept_handler]
        logging.getLogger(logger_name).setLevel(logging.DEBUG)
    
    # Настраиваем корневой logger
    logging.basicConfig(handlers=[intercept_handler], level=0, force=True)
    
    logger.info(f"Система логирования настроена для окружения: {config_name}")
    logger.info(f"Уровень логирования: {log_level}")
    logger.info(f"Директория логов: {os.path.abspath(LoggerConfig.LOG_DIR)}")


def get_logger(name: str = None):
    """
    Получение logger с определенным именем.
    
    Args:
        name: Имя logger'а
        
    Returns:
        loguru.Logger: Настроенный logger
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_request(response_status: int = None, response_size: int = None, duration: float = None):
    """
    Логирование HTTP запроса.
    
    Args:
        response_status: HTTP статус ответа
        response_size: Размер ответа в байтах
        duration: Длительность обработки запроса в секундах
    """
    if not has_request_context():
        return
    
    context = get_request_context()
    
    log_data = {
        "type": "REQUEST",
        "method": context.get("method"),
        "path": context.get("path"),
        "remote_addr": context.get("remote_addr"),
        "user_agent": context.get("user_agent", "")[:200],  # Ограничиваем размер
    }
    
    if response_status:
        log_data["status"] = response_status
    if response_size:
        log_data["size"] = response_size
    if duration:
        log_data["duration"] = round(duration, 3)
        if duration > 1.0:  # Медленные запросы
            log_data["slow"] = True
    
    # Форматируем сообщение
    message = f"REQUEST {log_data['method']} {log_data['path']} from {log_data['remote_addr']}"
    if response_status:
        message += f" -> {response_status}"
    if duration:
        message += f" ({duration:.3f}s)"
    
    # Уровень логирования в зависимости от статуса
    if response_status and response_status >= 500:
        logger.error(message, **log_data)
    elif response_status and response_status >= 400:
        logger.warning(message, **log_data)
    else:
        logger.info(message, **log_data)


def log_security_event(event_type: str, details: Dict[str, Any] = None, user_id: str = None):
    """
    Логирование событий безопасности.
    
    Args:
        event_type: Тип события (LOGIN, LOGOUT, AUTH_FAILED, etc.)
        details: Дополнительные детали события
        user_id: ID пользователя
    """
    context = get_request_context()
    
    log_data = {
        "type": "SECURITY",
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "remote_addr": context.get("remote_addr"),
        "user_agent": context.get("user_agent", "")[:200],
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if details:
        log_data.update(details)
    
    message = f"SECURITY {event_type}"
    if user_id:
        message += f" user:{user_id}"
    if context.get("remote_addr"):
        message += f" from {context['remote_addr']}"
    
    logger.warning(message, **log_data)


def log_admin_action(action: str, resource: str, resource_id: str = None, user_id: str = None, details: Dict[str, Any] = None):
    """
    Логирование действий в админке.
    
    Args:
        action: Действие (CREATE, UPDATE, DELETE, VIEW)
        resource: Ресурс (service, portfolio, user)
        resource_id: ID ресурса
        user_id: ID пользователя
        details: Дополнительные детали
    """
    context = get_request_context()
    
    log_data = {
        "type": "ADMIN",
        "action": action,
        "resource": resource,
        "timestamp": datetime.utcnow().isoformat(),
        "remote_addr": context.get("remote_addr"),
    }
    
    if resource_id:
        log_data["resource_id"] = resource_id
    if user_id:
        log_data["user_id"] = user_id
    if details:
        log_data.update(details)
    
    message = f"ADMIN {action} {resource}"
    if resource_id:
        message += f" id:{resource_id}"
    if user_id:
        message += f" by user:{user_id}"
    
    logger.info(message, **log_data)


def log_file_operation(operation: str, file_path: str, file_size: int = None, user_id: str = None, details: Dict[str, Any] = None):
    """
    Логирование файловых операций.
    
    Args:
        operation: Операция (UPLOAD, DELETE, OPTIMIZE, etc.)
        file_path: Путь к файлу
        file_size: Размер файла в байтах
        user_id: ID пользователя
        details: Дополнительные детали
    """
    context = get_request_context()
    
    log_data = {
        "type": "FILE",
        "operation": operation,
        "file_path": file_path,
        "timestamp": datetime.utcnow().isoformat(),
        "remote_addr": context.get("remote_addr"),
    }
    
    if file_size:
        log_data["file_size"] = file_size
        log_data["file_size_mb"] = round(file_size / (1024 * 1024), 2)
    if user_id:
        log_data["user_id"] = user_id
    if details:
        log_data.update(details)
    
    message = f"FILE {operation} {os.path.basename(file_path)}"
    if file_size:
        message += f" ({log_data['file_size_mb']}MB)"
    if user_id:
        message += f" by user:{user_id}"
    
    logger.info(message, **log_data)


def log_performance(operation: str, duration: float, details: Dict[str, Any] = None):
    """
    Логирование производительности.
    
    Args:
        operation: Операция
        duration: Длительность в секундах
        details: Дополнительные детали
    """
    log_data = {
        "type": "PERFORMANCE",
        "operation": operation,
        "duration": round(duration, 3),
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if details:
        log_data.update(details)
    
    message = f"PERFORMANCE {operation} took {duration:.3f}s"
    
    # Уровень логирования в зависимости от времени выполнения
    if duration > 5.0:
        logger.error(message, **log_data)
    elif duration > 2.0:
        logger.warning(message, **log_data)
    else:
        logger.info(message, **log_data) 