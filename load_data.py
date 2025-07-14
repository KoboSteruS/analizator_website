#!/usr/bin/env python3
"""
Скрипт для загрузки данных в базу данных.
Использует Flask контекст для работы с моделями.
"""

import os
import sys
from datetime import datetime

# Добавляем корневую директорию в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Service, Portfolio


def load_data():
    """Загрузка данных в БД."""
    
    # Создаём контекст приложения
    app = create_app('production')
    
    with app.app_context():
        try:
            print("🔄 Начинаем загрузку данных...")
            
            # Создаём таблицы если их нет
            db.create_all()
            print("✅ Таблицы созданы/проверены")
            
            # Загружаем пользователей
            load_users()
            
            # Загружаем услуги
            load_services()
            
            # Загружаем портфолио
            load_portfolio()
            
            # Сохраняем изменения
            db.session.commit()
            print("✅ Все данные успешно загружены!")
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            db.session.rollback()
            raise


def load_users():
    """Загрузка пользователей."""
    print("📁 Загружаем пользователей...")
    
    # Проверяем есть ли уже суперпользователь
    existing_user = User.query.filter_by(email='admin@example.com').first()
    if existing_user:
        print("  ℹ️  Суперпользователь уже существует")
        return
    
    # Создаём суперпользователя
    admin_user = User(
        email='admin@example.com',
        full_name='Администратор',
        is_superuser=True,
        is_active=True
    )
    admin_user.set_password('password123')
    admin_user.generate_jwt_secret()
    
    db.session.add(admin_user)
    print("  ✅ Суперпользователь создан")


def load_services():
    """Загрузка услуг."""
    print("📁 Загружаем услуги...")
    
    services_data = [
        {
            'title': 'Разработка веб-сайтов',
            'description': 'Создание современных и функциональных веб-сайтов',
            'short_description': 'Профессиональная разработка сайтов',
            'price': 50000.0,
            'category': 'development',
            'is_featured': True,
            'icon': 'fas fa-laptop-code'
        },
        {
            'title': 'SEO оптимизация',
            'description': 'Поисковая оптимизация для увеличения трафика',
            'short_description': 'Вывод сайта в ТОП поисковых систем',
            'price': 30000.0,
            'category': 'marketing',
            'is_featured': True,
            'icon': 'fas fa-search'
        },
        {
            'title': 'Настройка рекламы',
            'description': 'Настройка и ведение рекламных кампаний',
            'short_description': 'Эффективная контекстная реклама',
            'price': 25000.0,
            'category': 'marketing',
            'is_featured': False,
            'icon': 'fas fa-bullhorn'
        }
    ]
    
    for service_data in services_data:
        # Проверяем есть ли уже такая услуга
        existing_service = Service.query.filter_by(title=service_data['title']).first()
        if existing_service:
            print(f"  ℹ️  Услуга '{service_data['title']}' уже существует")
            continue
            
        service = Service(**service_data)
        db.session.add(service)
        print(f"  ✅ Услуга '{service_data['title']}' добавлена")


def load_portfolio():
    """Загрузка портфолио."""
    print("📁 Загружаем портфолио...")
    
    portfolio_data = [
        {
            'title': 'Интернет-магазин электроники',
            'description': 'Разработка полнофункционального интернет-магазина с каталогом товаров, корзиной и системой оплаты',
            'client': 'ООО "ТехМаркет"',
            'location': 'Москва',
            'category': 'ecommerce',
            'price': 150000.0,
            'completion_date': datetime(2024, 6, 15),
            'is_featured': True,
            'technologies': '["Python", "Flask", "PostgreSQL", "Redis", "Bootstrap"]',
            'status': 'completed'
        },
        {
            'title': 'Корпоративный сайт строительной компании',
            'description': 'Создание корпоративного сайта с портфолио проектов и системой управления контентом',
            'client': 'СтройПроект',
            'location': 'Санкт-Петербург',
            'category': 'corporate',
            'price': 80000.0,
            'completion_date': datetime(2024, 5, 20),
            'is_featured': True,
            'technologies': '["HTML5", "CSS3", "JavaScript", "PHP", "MySQL"]',
            'status': 'completed'
        },
        {
            'title': 'Система управления складом',
            'description': 'Веб-приложение для учёта товаров на складе с функциями инвентаризации и отчётности',
            'client': 'Логистик Плюс',
            'location': 'Екатеринбург',
            'category': 'webapp',
            'price': 120000.0,
            'completion_date': datetime(2024, 7, 10),
            'is_featured': False,
            'technologies': '["Python", "Django", "PostgreSQL", "Celery", "Vue.js"]',
            'status': 'completed'
        }
    ]
    
    for portfolio_item in portfolio_data:
        # Проверяем есть ли уже такой проект
        existing_project = Portfolio.query.filter_by(title=portfolio_item['title']).first()
        if existing_project:
            print(f"  ℹ️  Проект '{portfolio_item['title']}' уже существует")
            continue
            
        project = Portfolio(**portfolio_item)
        db.session.add(project)
        print(f"  ✅ Проект '{portfolio_item['title']}' добавлен")


if __name__ == '__main__':
    load_data() 