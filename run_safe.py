"""
Безопасная точка входа в Flask приложение.
Улучшенная версия с обработкой ошибок и диагностикой.
"""

import os
import sys
import traceback
from pathlib import Path

def setup_environment():
    """Настройка переменных окружения."""
    # Загружаем .env файл если он есть
    env_file = Path('.env')
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ .env файл загружен")
        except ImportError:
            print("⚠️ python-dotenv не установлен, .env файл не загружен")
    
    # Устанавливаем FLASK_ENV если не установлено
    if not os.getenv('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
        print(f"✅ FLASK_ENV установлен в: {os.environ['FLASK_ENV']}")

def create_application():
    """Создание Flask приложения с обработкой ошибок."""
    try:
        # Настройка окружения
        setup_environment()
        
        # Импорт функции создания приложения
        print("🔄 Импорт create_app...")
        from app import create_app
        
        # Получение режима из переменной окружения
        config_name = os.getenv('FLASK_ENV', 'production')
        print(f"🔄 Создание приложения для окружения: {config_name}")
        
        # Создание приложения
        app = create_app(config_name)
        
        print(f"✅ Приложение создано успешно")
        print(f"   - Название: {app.name}")
        print(f"   - Конфигурация: {app.config.get('ENV', 'неизвестно')}")
        print(f"   - Debug режим: {app.config.get('DEBUG', False)}")
        
        return app
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте установку зависимостей:")
        print("  pip install -r requirements.txt")
        traceback.print_exc()
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        print("Запустите диагностику: python3 diagnose_gunicorn.py")
        traceback.print_exc()
        sys.exit(1)

# Создание приложения
print("🚀 Запуск Flask приложения...")
app = create_application()

if __name__ == '__main__':
    """Запуск приложения в режиме разработки."""
    
    try:
        print("🔄 Запуск в режиме разработки...")
        
        # Настройки для разработки
        host = os.getenv('FLASK_HOST', '127.0.0.1')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_ENV', 'development') == 'development'
        
        print(f"🌐 Приложение будет доступно по адресу: http://{host}:{port}")
        print(f"🐛 Debug режим: {debug}")
        
        app.run(
            host=host,
            port=port,
            debug=debug
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        traceback.print_exc()
        sys.exit(1) 