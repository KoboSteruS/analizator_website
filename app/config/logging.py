"""
Конфигурация логирования для разных окружений.
Настройка уровней логирования и дополнительных параметров.
"""

import os
from typing import Dict, Any


class LoggingConfig:
    """Базовая конфигурация логирования."""
    
    # Директория для логов
    LOG_DIR = "logs"
    
    # Общие настройки
    DEFAULT_ROTATION = "10 MB"
    DEFAULT_RETENTION = "30 days"
    
    # Настройки компрессии
    COMPRESSION = "gz"
    
    # Базовый уровень логирования
    DEFAULT_LEVEL = "INFO"


class DevelopmentLoggingConfig(LoggingConfig):
    """Конфигурация логирования для разработки."""
    
    # Более подробное логирование в разработке
    DEFAULT_LEVEL = "DEBUG"
    
    # Настройки файлов логов
    LOG_FILES = {
        'app': {
            'level': 'DEBUG',
            'rotation': '50 MB',
            'retention': '7 days'
        },
        'requests': {
            'level': 'DEBUG',
            'rotation': '100 MB',
            'retention': '3 days'
        },
        'database': {
            'level': 'DEBUG',
            'rotation': '50 MB',
            'retention': '3 days'
        },
        'errors': {
            'level': 'ERROR',
            'retention': '14 days'
        },
        'security': {
            'level': 'INFO',
            'retention': '60 days'
        },
        'admin': {
            'level': 'INFO',
            'retention': '30 days'
        },
        'files': {
            'level': 'INFO',
            'retention': '14 days'
        },
        'performance': {
            'level': 'INFO',
            'retention': '7 days'
        }
    }
    
    # Настройки консоли
    CONSOLE = {
        'enabled': True,
        'level': 'DEBUG',
        'colorize': True,
        'format': 'detailed'
    }
    
    # Дополнительные настройки
    BACKTRACE = True
    DIAGNOSE = True
    ENQUEUE = False  # Для разработки синхронно
    
    # SQLAlchemy логирование
    SQLALCHEMY_ECHO = True


class ProductionLoggingConfig(LoggingConfig):
    """Конфигурация логирования для продакшена."""
    
    # Минимальное логирование в продакшене
    DEFAULT_LEVEL = "WARNING"
    
    # Настройки файлов логов
    LOG_FILES = {
        'app': {
            'level': 'INFO',
            'rotation': '100 MB',
            'retention': '60 days'
        },
        'requests': {
            'level': 'INFO',
            'rotation': '200 MB',
            'retention': '30 days'
        },
        'database': {
            'level': 'WARNING',
            'rotation': '50 MB',
            'retention': '14 days'
        },
        'errors': {
            'level': 'ERROR',
            'retention': '90 days'
        },
        'security': {
            'level': 'WARNING',
            'retention': '180 days'  # Дольше храним логи безопасности
        },
        'admin': {
            'level': 'INFO',
            'retention': '90 days'
        },
        'files': {
            'level': 'INFO',
            'retention': '60 days'
        },
        'performance': {
            'level': 'WARNING',
            'retention': '30 days'
        }
    }
    
    # Настройки консоли
    CONSOLE = {
        'enabled': False,  # Отключаем консольный вывод в продакшене
        'level': 'ERROR',
        'colorize': False,
        'format': 'simple'
    }
    
    # Дополнительные настройки
    BACKTRACE = False  # Отключаем backtrace в продакшене
    DIAGNOSE = False   # Отключаем diagnose в продакшене
    ENQUEUE = True     # Асинхронное логирование в продакшене
    
    # SQLAlchemy логирование
    SQLALCHEMY_ECHO = False


class TestingLoggingConfig(LoggingConfig):
    """Конфигурация логирования для тестирования."""
    
    # Минимальное логирование в тестах
    DEFAULT_LEVEL = "ERROR"
    
    # Настройки файлов логов
    LOG_FILES = {
        'app': {
            'level': 'ERROR',
            'rotation': '10 MB',
            'retention': '1 day'
        },
        'errors': {
            'level': 'ERROR',
            'retention': '1 day'
        },
        'security': {
            'level': 'WARNING',
            'retention': '3 days'
        }
    }
    
    # Настройки консоли
    CONSOLE = {
        'enabled': False,  # Отключаем консольный вывод в тестах
        'level': 'ERROR',
        'colorize': False,
        'format': 'simple'
    }
    
    # Дополнительные настройки
    BACKTRACE = False
    DIAGNOSE = False
    ENQUEUE = False  # Синхронно в тестах
    
    # SQLAlchemy логирование
    SQLALCHEMY_ECHO = False


# Словарь конфигураций логирования
LOGGING_CONFIG: Dict[str, Any] = {
    'development': DevelopmentLoggingConfig,
    'production': ProductionLoggingConfig,
    'testing': TestingLoggingConfig,
    'default': DevelopmentLoggingConfig
}


def get_logging_config(environment: str = None) -> Any:
    """
    Получение конфигурации логирования для окружения.
    
    Args:
        environment: Название окружения
        
    Returns:
        Класс конфигурации логирования
    """
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    return LOGGING_CONFIG.get(environment, LOGGING_CONFIG['default'])


# Настройки фильтров для логов
LOG_FILTERS = {
    'security': [
        'AUTH', 'LOGIN', 'LOGOUT', 'SECURITY', 'ADMIN', 
        'JWT', 'UNAUTHORIZED', 'FORBIDDEN', 'ACCESS'
    ],
    'admin': [
        'ADMIN', 'CREATE', 'UPDATE', 'DELETE', 'MANAGE'
    ],
    'files': [
        'UPLOAD', 'DOWNLOAD', 'FILE', 'IMAGE', 'DELETE', 
        'OPTIMIZE', 'THUMBNAIL'
    ],
    'performance': [
        'SLOW', 'PERFORMANCE', 'TIME', 'DURATION', 
        'LATENCY', 'TIMEOUT'
    ],
    'requests': [
        'REQUEST', 'RESPONSE', 'GET', 'POST', 'PUT', 
        'DELETE', 'PATCH'
    ]
}


# Чувствительные данные для маскировки в логах
SENSITIVE_FIELDS = [
    'password', 'token', 'secret', 'key', 'auth', 
    'authorization', 'cookie', 'session', 'csrf'
]


# Настройки уведомлений (для будущего расширения)
NOTIFICATION_CONFIG = {
    'email': {
        'enabled': False,
        'levels': ['ERROR', 'CRITICAL'],
        'recipients': []
    },
    'webhook': {
        'enabled': False,
        'url': None,
        'levels': ['ERROR', 'CRITICAL']
    }
} 