#!/usr/bin/env python3
"""
Скрипт для создания суперпользователя и инициализации данных.
Создает администратора с уникальным JWT ключом для доступа к админке.
"""

import os
import sys
from getpass import getpass

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Service, Portfolio
from app.routes.admin import refresh_admin_routes
from loguru import logger


def create_test_superuser():
    """Создание тестового суперпользователя с предустановленными данными."""
    app = create_app()
    
    with app.app_context():
        print("=== Создание тестового суперпользователя ===\n")
        
        # Создаем таблицы если их нет
        db.create_all()
        
        email = "admin@example.com"
        password = "password123"
        full_name = "Администратор"
        
        # Проверяем существующего пользователя
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ Пользователь с email {email} уже существует")
            print(f"🔑 JWT ключ: {existing_user.jwt_secret}")
            print(f"🌐 URL админки: http://127.0.0.1:5000/{existing_user.jwt_secret}/admin")
            return
        
        try:
            # Создаем суперпользователя
            user = User.create_superuser(
                email=email,
                password=password,
                full_name=full_name
            )
            
            db.session.add(user)
            db.session.commit()
            
            print(f"✅ Тестовый суперпользователь создан успешно!")
            print(f"📧 Email: {user.email}")
            print(f"🔑 Пароль: {password}")
            print(f"👤 Имя: {user.full_name}")
            print(f"🔑 JWT ключ: {user.jwt_secret}")
            print(f"🌐 URL админки: http://127.0.0.1:5000/{user.jwt_secret}/admin")
            
            # Перерегистрируем админ роуты
            refresh_admin_routes(app)
            print("🔄 Админ роуты обновлены")
            
            logger.info(f"Создан тестовый суперпользователь: {user.email}")
            
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            db.session.rollback()


def create_superuser():
    """Создание суперпользователя."""
    app = create_app()
    
    with app.app_context():
        print("=== Создание суперпользователя ===\n")
        
        # Создаем таблицы если их нет
        db.create_all()
        
        # Проверяем существующих суперпользователей
        existing_superusers = User.query.filter_by(is_superuser=True).all()
        if existing_superusers:
            print("Существующие суперпользователи:")
            for user in existing_superusers:
                print(f"  - {user.email} (JWT: /{user.jwt_secret}/admin)")
            print()
        
        # Запрашиваем данные нового пользователя
        email = input("Email администратора: ").strip()
        if not email:
            print("❌ Email не может быть пустым")
            return
        
        # Проверяем уникальность email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ Пользователь с email {email} уже существует")
            return
        
        password = getpass("Пароль администратора: ")
        if not password:
            print("❌ Пароль не может быть пустым")
            return
        
        password_confirm = getpass("Подтвердите пароль: ")
        if password != password_confirm:
            print("❌ Пароли не совпадают")
            return
        
        full_name = input("Полное имя (необязательно): ").strip()
        
        try:
            # Создаем суперпользователя
            user = User.create_superuser(
                email=email,
                password=password,
                full_name=full_name or "Администратор"
            )
            
            db.session.add(user)
            db.session.commit()
            
            print(f"\n✅ Суперпользователь создан успешно!")
            print(f"📧 Email: {user.email}")
            print(f"👤 Имя: {user.full_name}")
            print(f"🔑 JWT ключ: {user.jwt_secret}")
            print(f"🌐 URL админки: http://127.0.0.1:5000/{user.jwt_secret}/admin")
            print(f"\n⚠️  ВАЖНО: Сохраните JWT ключ в безопасном месте!")
            
            # Перерегистрируем админ роуты
            refresh_admin_routes(app)
            print("🔄 Админ роуты обновлены")
            
            logger.info(f"Создан суперпользователь: {user.email}")
            
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            db.session.rollback()


def init_default_data():
    """Инициализация данных по умолчанию."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Инициализация данных по умолчанию ===\n")
        
        # Создаем таблицы
        db.create_all()
        
        # Создаем услуги по умолчанию
        services = Service.create_default_services()
        if services:
            for service in services:
                db.session.add(service)
            db.session.commit()
            print(f"✅ Создано {len(services)} услуг по умолчанию")
        else:
            print("ℹ️  Услуги уже существуют")
        
        # Создаем проекты портфолио по умолчанию
        projects = Portfolio.create_default_portfolio()
        if projects:
            for project in projects:
                db.session.add(project)
            db.session.commit()
            print(f"✅ Создано {len(projects)} проектов портфолио по умолчанию")
        else:
            print("ℹ️  Проекты портфолио уже существуют")


def regenerate_jwt_secret():
    """Перегенерация JWT секрета для пользователя."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Перегенерация JWT ключа ===\n")
        
        users = User.query.filter_by(is_superuser=True).all()
        if not users:
            print("❌ Суперпользователи не найдены")
            return
        
        print("Доступные пользователи:")
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user.email}")
        
        try:
            choice = int(input("\nВыберите пользователя (номер): ")) - 1
            if choice < 0 or choice >= len(users):
                print("❌ Неверный выбор")
                return
            
            user = users[choice]
            old_secret = user.jwt_secret
            new_secret = user.regenerate_jwt_secret()
            
            db.session.commit()
            
            print(f"\n✅ JWT ключ обновлен для {user.email}")
            print(f"🔑 Старый ключ: {old_secret}")
            print(f"🔑 Новый ключ: {new_secret}")
            print(f"🌐 Новый URL админки: http://127.0.0.1:5000/{new_secret}/admin")
            
            # Перерегистрируем админ роуты
            refresh_admin_routes(app)
            print("🔄 Админ роуты обновлены")
            
            logger.info(f"JWT ключ обновлен для пользователя: {user.email}")
            
        except (ValueError, IndexError):
            print("❌ Неверный выбор")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()


def list_superusers():
    """Список всех суперпользователей."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Список суперпользователей ===\n")
        
        users = User.query.filter_by(is_superuser=True).all()
        if not users:
            print("❌ Суперпользователи не найдены")
            return
        
        for user in users:
            status = "🟢 Активен" if user.is_active else "🔴 Неактивен"
            last_login = user.last_login.strftime('%d.%m.%Y %H:%M') if user.last_login else "Никогда"
            
            print(f"📧 Email: {user.email}")
            print(f"👤 Имя: {user.full_name}")
            print(f"🔑 JWT: {user.jwt_secret}")
            print(f"🌐 URL: http://127.0.0.1:5000/{user.jwt_secret}/admin")
            print(f"📊 Статус: {status}")
            print(f"🕐 Последний вход: {last_login}")
            print("-" * 50)


def main():
    """Главная функция."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_superuser()
        elif command == "test":
            create_test_superuser()
        elif command == "init":
            init_default_data()
        elif command == "regenerate":
            regenerate_jwt_secret()
        elif command == "list":
            list_superusers()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print_help()
    else:
        print("🔧 Менеджер суперпользователей LendingAnalyzer")
        print("\nВыберите действие:")
        print("1. Создать суперпользователя")
        print("2. Создать тестового суперпользователя (admin@example.com)")
        print("3. Инициализировать данные по умолчанию")
        print("4. Перегенерировать JWT ключ")
        print("5. Список суперпользователей")
        print("0. Выход")
        
        try:
            choice = input("\nВаш выбор: ").strip()
            
            if choice == "1":
                create_superuser()
            elif choice == "2":
                create_test_superuser()
            elif choice == "3":
                init_default_data()
            elif choice == "4":
                regenerate_jwt_secret()
            elif choice == "5":
                list_superusers()
            elif choice == "0":
                print("👋 До свидания!")
                return
            else:
                print("❌ Неверный выбор")
        except KeyboardInterrupt:
            print("\n\n👋 Прервано пользователем")


def print_help():
    """Справка по командам."""
    print("\nИспользование:")
    print("  python create_superuser.py [команда]")
    print("\nКоманды:")
    print("  create      - Создать нового суперпользователя")
    print("  test        - Создать тестового суперпользователя (admin@example.com)")
    print("  init        - Инициализировать данные по умолчанию")
    print("  regenerate  - Перегенерировать JWT ключ")
    print("  list        - Показать всех суперпользователей")
    print("\nБез команды запускается интерактивный режим.")


if __name__ == "__main__":
    main() 