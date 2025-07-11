"""
Точка входа в Flask приложение.
Запуск приложения для разработки и продакшена.
"""

import os
from dotenv import load_dotenv
from app import create_app
from loguru import logger

# Загрузка переменных окружения
load_dotenv()

# Создание приложения
app = create_app()

if __name__ == '__main__':
    """Запуск приложения в режиме разработки."""
    
    logger.info("Запуск Flask приложения в режиме разработки")
    
    # Настройки для разработки
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Приложение будет доступно по адресу: http://{host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    ) 