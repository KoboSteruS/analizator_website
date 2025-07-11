"""
Фабрика Flask приложения.
Инициализация приложения и всех расширений.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from loguru import logger
import os
from typing import Optional

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Фабрика приложения Flask.
    
    Args:
        config_name: Название конфигурации (development, production, testing)
        
    Returns:
        Flask: Настроенное приложение Flask
    """
    app = Flask(__name__)
    
    # Загрузка конфигурации
    from app.config import config_by_name
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config_by_name[config_name])
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Настройка логирования
    setup_logging(app)
    
    # Регистрация blueprints
    register_blueprints(app)
    
    # Обработчики ошибок
    register_error_handlers(app)
    
    logger.info(f"Flask приложение создано с конфигурацией: {config_name}")
    
    return app


def setup_logging(app: Flask) -> None:
    """Настройка логирования через loguru."""
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True
    )
    
    if app.config.get('DEBUG'):
        logger.add(
            "logs/debug.log",
            rotation="100 MB",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
        )


def register_blueprints(app: Flask) -> None:
    """Регистрация всех blueprints."""
    from app.routes import main_bp
    from app.routes.admin import register_admin_routes
    
    app.register_blueprint(main_bp)
    
    # Регистрируем админку
    register_admin_routes(app)


def register_error_handlers(app: Flask) -> None:
    """Регистрация обработчиков ошибок."""
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 ошибка: {error}")
        return {"error": "Ресурс не найден"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 ошибка: {error}")
        db.session.rollback()
        return {"error": "Внутренняя ошибка сервера"}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"400 ошибка: {error}")
        return {"error": "Неверный запрос"}, 400 