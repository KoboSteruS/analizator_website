#!/usr/bin/env python3
"""
Скрипт для настройки системы миграций Flask-Migrate.
"""

import os
import sys

# Добавляем корневую директорию в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from flask_migrate import Migrate, init, migrate, upgrade


def setup_migrations():
    """Настройка системы миграций."""
    
    app = create_app('production')
    migrate = Migrate(app, db)
    
    with app.app_context():
        try:
            print("🔄 Настройка системы миграций...")
            
            # Проверяем есть ли уже папка migrations
            if not os.path.exists('migrations'):
                print("📁 Инициализируем миграции...")
                init()
                print("✅ Миграции инициализированы")
            else:
                print("ℹ️  Система миграций уже настроена")
            
            # Создаём миграцию из текущего состояния БД
            print("📝 Создаём миграцию...")
            migrate(message="Initial migration")
            print("✅ Миграция создана")
            
            # Применяем миграцию
            print("🚀 Применяем миграции...")
            upgrade()
            print("✅ Миграции применены")
            
            print("🎉 Система миграций успешно настроена!")
            
        except Exception as e:
            print(f"❌ Ошибка при настройке миграций: {e}")
            if "already exists" in str(e).lower():
                print("ℹ️  Миграции уже настроены")
            else:
                raise


if __name__ == '__main__':
    setup_migrations() 