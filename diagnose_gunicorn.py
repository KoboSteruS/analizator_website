#!/usr/bin/env python3
"""
Диагностический скрипт для проблем с gunicorn.
Проверяет все зависимости и компоненты перед запуском.
"""

import os
import sys
import traceback
from pathlib import Path

def check_python_path():
    """Проверка Python path."""
    print("🔍 Проверка Python path...")
    print(f"Python версия: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")
    print()

def check_environment():
    """Проверка переменных окружения."""
    print("🔍 Проверка переменных окружения...")
    env_vars = ['FLASK_ENV', 'FLASK_APP', 'DATABASE_URL', 'SECRET_KEY']
    for var in env_vars:
        value = os.getenv(var, 'НЕ УСТАНОВЛЕНА')
        if var == 'SECRET_KEY' and value != 'НЕ УСТАНОВЛЕНА':
            value = '***СКРЫТО***'
        print(f"{var}: {value}")
    print()

def check_basic_imports():
    """Проверка базовых импортов."""
    print("🔍 Проверка базовых импортов...")
    
    basic_modules = [
        'flask', 'loguru', 'sqlalchemy', 'flask_migrate', 
        'flask_jwt_extended', 'dotenv'
    ]
    
    for module in basic_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
    print()

def check_app_structure():
    """Проверка структуры приложения."""
    print("🔍 Проверка структуры приложения...")
    
    required_files = [
        'app/__init__.py',
        'app/config/__init__.py',
        'app/config/logging.py',
        'app/utils/__init__.py',
        'app/utils/logging.py',
        'app/models/__init__.py',
        'app/routes/__init__.py',
        'run.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")
    print()

def check_app_imports():
    """Проверка импортов приложения."""
    print("🔍 Проверка импортов приложения...")
    
    try:
        print("Импорт app.config.logging...")
        from app.config.logging import get_logging_config
        print("✅ app.config.logging импортирован")
        
        config = get_logging_config('production')
        print(f"✅ Конфигурация получена: {config}")
        
    except Exception as e:
        print(f"❌ Ошибка импорта app.config.logging: {e}")
        traceback.print_exc()
    
    try:
        print("Импорт app.utils.logging...")
        from app.utils.logging import setup_logging
        print("✅ app.utils.logging импортирован")
        
    except Exception as e:
        print(f"❌ Ошибка импорта app.utils.logging: {e}")
        traceback.print_exc()
    
    try:
        print("Импорт app...")
        from app import create_app
        print("✅ app импортирован")
        
    except Exception as e:
        print(f"❌ Ошибка импорта app: {e}")
        traceback.print_exc()
    
    print()

def check_app_creation():
    """Проверка создания приложения."""
    print("🔍 Проверка создания приложения...")
    
    try:
        # Устанавливаем переменную окружения для продакшена
        os.environ['FLASK_ENV'] = 'production'
        
        print("Импорт create_app...")
        from app import create_app
        
        print("Создание приложения...")
        app = create_app('production')
        
        print(f"✅ Приложение создано: {app}")
        print(f"✅ Название приложения: {app.name}")
        print(f"✅ Конфигурация: {app.config.get('ENV', 'НЕ ОПРЕДЕЛЕНА')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        traceback.print_exc()
        return False

def check_gunicorn_compatibility():
    """Проверка совместимости с gunicorn."""
    print("🔍 Проверка совместимости с gunicorn...")
    
    try:
        import gunicorn
        print(f"✅ Gunicorn установлен: {gunicorn.__version__}")
        
        # Проверим что run.py работает как модуль
        print("Проверка run:app...")
        import run
        app = getattr(run, 'app', None)
        if app:
            print("✅ run:app доступен")
        else:
            print("❌ run:app НЕ найден")
            
    except ImportError:
        print("❌ Gunicorn не установлен")
    except Exception as e:
        print(f"❌ Ошибка проверки gunicorn: {e}")
        traceback.print_exc()
    print()

def main():
    """Основная функция диагностики."""
    print("=" * 60)
    print("🩺 ДИАГНОСТИКА ПРОБЛЕМ С GUNICORN")
    print("=" * 60)
    print()
    
    check_python_path()
    check_environment()
    check_basic_imports()
    check_app_structure()
    check_app_imports()
    
    if check_app_creation():
        print("✅ Базовая проверка пройдена!")
    else:
        print("❌ Критическая ошибка - приложение не может быть создано!")
        return False
    
    check_gunicorn_compatibility()
    
    print("=" * 60)
    print("🎯 РЕКОМЕНДАЦИИ:")
    print("1. Если есть ошибки импорта - исправьте их")
    print("2. Убедитесь что FLASK_ENV=production")
    print("3. Попробуйте запустить: python3 diagnose_gunicorn.py")
    print("4. Затем: gunicorn --bind 127.0.0.1:8000 run:app")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Диагностика прервана пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка диагностики: {e}")
        traceback.print_exc() 