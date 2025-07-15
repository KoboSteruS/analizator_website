"""
Конфигурация Flask приложения.
Настройки для разных окружений: development, production, testing.
"""

import os
from datetime import timedelta
from typing import Dict, Type


class Config:
    """Базовый класс конфигурации."""
    
    # Секретный ключ
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT настройки
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки загрузки файлов
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
    
    # Другие настройки
    JSON_AS_ASCII = False  # Поддержка UTF-8 в JSON ответах
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    
    DEBUG = True
    TESTING = False
    
    # SQLite для разработки
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev.db'
    
    # Расширенное логирование
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    
    DEBUG = False
    TESTING = False
    
    # PostgreSQL для продакшена
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:pass@localhost/lending_analyzer'
    
    # Безопасность
    SQLALCHEMY_ECHO = False
    
    # Проверка обязательных переменных окружения
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Проверка секретных ключей
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY должен быть установлен в продакшене")
        
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ValueError("JWT_SECRET_KEY должен быть установлен в продакшене")


class TestingConfig(Config):
    """Конфигурация для тестирования."""
    
    DEBUG = False
    TESTING = True
    
    # Тестовая база данных в памяти
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Отключение CSRF для тестов
    WTF_CSRF_ENABLED = False
    
    # Быстрые хеши для тестов
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=1)


# Словарь конфигураций
config_by_name: Dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 