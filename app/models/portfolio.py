"""
Модель портфолио для админки.
Содержит информацию о проектах компании.
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime
from app.models.base import BaseModel
from datetime import datetime


class Portfolio(BaseModel):
    """
    Модель проекта портфолио.
    
    Поля:
    - title: Название проекта
    - description: Описание проекта
    - client: Название клиента
    - location: Местоположение
    - category: Категория проекта
    - image_url: URL изображения проекта
    - project_url: URL проекта (если есть)
    - price: Цена проекта
    - completion_date: Дата завершения
    - is_featured: Флаг избранного проекта
    - is_active: Флаг активности
    - sort_order: Порядок сортировки
    - technologies: Используемые технологии (JSON)
    - status: Статус проекта
    """
    
    __tablename__ = 'portfolio'
    
    title = Column(
        String(200),
        nullable=False,
        comment="Название проекта"
    )
    
    description = Column(
        Text,
        nullable=False,
        comment="Описание проекта"
    )
    
    client = Column(
        String(200),
        nullable=False,
        comment="Название клиента"
    )
    
    location = Column(
        String(100),
        nullable=True,
        comment="Местоположение"
    )
    
    category = Column(
        String(100),
        nullable=False,
        comment="Категория проекта"
    )
    
    image_url = Column(
        String(500),
        nullable=True,
        comment="URL изображения проекта"
    )
    
    project_url = Column(
        String(500),
        nullable=True,
        comment="URL проекта"
    )
    
    price = Column(
        Float,
        nullable=True,
        comment="Цена проекта (в рублях)"
    )
    
    completion_date = Column(
        DateTime,
        nullable=True,
        comment="Дата завершения проекта"
    )
    
    is_featured = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Флаг избранного проекта"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Флаг активности"
    )
    
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Порядок сортировки"
    )
    
    technologies = Column(
        Text,
        nullable=True,
        comment="Используемые технологии (JSON)"
    )
    
    status = Column(
        String(50),
        default="completed",
        nullable=False,
        comment="Статус проекта"
    )
    
    class Status:
        """Статусы проектов."""
        COMPLETED = "completed"
        IN_PROGRESS = "in_progress"
        PLANNED = "planned"
        CANCELLED = "cancelled"
    
    class Category:
        """Категории проектов."""
        SYSTEM_ACCOUNTING = "Система учета"
        AUTOMATION = "Автоматизация"
        SMS_SERVICE = "SMS-сервис"
        ANALYTICS = "Аналитика"
        MARKETPLACE = "Маркетплейс"
        OTHER = "Другое"
    
    @classmethod
    def get_active(cls):
        """
        Получение всех активных проектов с сортировкой.
        
        Returns:
            List[Portfolio]: Список активных проектов
        """
        return cls.query.filter_by(is_active=True).order_by(cls.sort_order.desc(), cls.completion_date.desc()).all()
    
    @classmethod
    def get_featured(cls):
        """
        Получение избранных проектов.
        
        Returns:
            List[Portfolio]: Список избранных проектов
        """
        return cls.query.filter_by(is_active=True, is_featured=True).order_by(cls.sort_order.desc()).all()
    
    @classmethod
    def create_default_portfolio(cls):
        """Создание проектов портфолио по умолчанию."""
        default_projects = [
            {
                'title': '1С:Analizator',
                'description': 'Комплексное решение управленческого учета селлеров маркетплейсов. Автоматизация финансового учета, интеграция с популярными площадками.',
                'client': 'AnalizatorMP',
                'location': 'Россия',
                'category': cls.Category.SYSTEM_ACCOUNTING,
                'price': 150000,
                'completion_date': datetime(2024, 2, 1),
                'is_featured': True,
                'sort_order': 3,
                'status': cls.Status.COMPLETED,
                'technologies': '["1С:Предприятие", "REST API", "JSON", "SQL Server"]'
            },
            {
                'title': 'Analizator MP',
                'description': 'Автоматизация бизнес-процессов для маркетплейсов. Управление товарами, заказами, финансами и аналитикой продаж.',
                'client': 'AnalizatorMP',
                'location': 'Россия',
                'category': cls.Category.AUTOMATION,
                'price': 300000,
                'completion_date': datetime(2024, 1, 15),
                'is_featured': True,
                'sort_order': 2,
                'status': cls.Status.COMPLETED,
                'technologies': '["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"]'
            },
            {
                'title': 'SMS Analizator',
                'description': 'Решение для доступа персонала к кодам из SMS. Безопасная передача SMS-кодов сотрудникам для работы с маркетплейсами.',
                'client': 'AnalizatorMP',
                'location': 'Россия',
                'category': cls.Category.SMS_SERVICE,
                'price': 50000,
                'completion_date': datetime(2024, 1, 10),
                'is_featured': True,
                'sort_order': 1,
                'status': cls.Status.COMPLETED,
                'technologies': '["Node.js", "Express", "MongoDB", "WebSocket", "Telegram API"]'
            },
            {
                'title': 'Дашборд аналитики Wildberries',
                'description': 'Система аналитики и отчетности для селлеров Wildberries. Визуализация продаж, прибыли и KPI в реальном времени.',
                'client': 'ООО "ТорговыйДом"',
                'location': 'Москва',
                'category': cls.Category.ANALYTICS,
                'price': 120000,
                'completion_date': datetime(2024, 1, 5),
                'is_featured': False,
                'sort_order': 4,
                'status': cls.Status.COMPLETED,
                'technologies': '["React", "D3.js", "Python", "Pandas", "Wildberries API"]'
            },
            {
                'title': 'Автоматизация OZON',
                'description': 'Комплексная автоматизация процессов работы с маркетплейсом OZON. Управление товарами, ценами и складскими остатками.',
                'client': 'ИП Сидоров А.В.',
                'location': 'Санкт-Петербург',
                'category': cls.Category.MARKETPLACE,
                'price': 85000,
                'completion_date': datetime(2023, 12, 20),
                'is_featured': False,
                'sort_order': 5,
                'status': cls.Status.COMPLETED,
                'technologies': '["Python", "OZON API", "Celery", "Redis", "PostgreSQL"]'
            }
        ]
        
        created_projects = []
        for project_data in default_projects:
            # Проверяем, не существует ли уже такой проект
            existing = cls.query.filter_by(title=project_data['title']).first()
            if not existing:
                project = cls(**project_data)
                created_projects.append(project)
        
        return created_projects
    
    def to_dict(self) -> dict:
        """
        Преобразование в словарь.
        
        Returns:
            dict: Данные проекта
        """
        data = super().to_dict()
        
        # Парсим JSON технологии если есть
        if self.technologies:
            try:
                import json
                data['technologies_list'] = json.loads(self.technologies)
            except:
                data['technologies_list'] = []
        else:
            data['technologies_list'] = []
        
        # Форматируем дату
        if self.completion_date:
            data['completion_date_formatted'] = self.completion_date.strftime('%d %b %Y')
        else:
            data['completion_date_formatted'] = None
        
        # Форматируем цену
        if self.price:
            data['price_formatted'] = f"₽{self.price:,.0f}".replace(',', ' ')
        else:
            data['price_formatted'] = None
        
        return data
    
    def set_technologies(self, technologies_list: list) -> None:
        """
        Установка списка технологий.
        
        Args:
            technologies_list: Список технологий
        """
        import json
        self.technologies = json.dumps(technologies_list, ensure_ascii=False)
    
    def get_technologies(self) -> list:
        """
        Получение списка технологий.
        
        Returns:
            list: Список технологий
        """
        if not self.technologies:
            return []
        
        try:
            import json
            return json.loads(self.technologies)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_category_color(self) -> str:
        """
        Получение цвета для категории.
        
        Returns:
            str: HEX цвет для категории
        """
        colors = {
            self.Category.SYSTEM_ACCOUNTING: "#8B5CF6",
            self.Category.AUTOMATION: "#EC4899", 
            self.Category.SMS_SERVICE: "#F59E0B",
            self.Category.ANALYTICS: "#10B981",
            self.Category.MARKETPLACE: "#EF4444",
            self.Category.OTHER: "#6B7280"
        }
        return colors.get(self.category, "#6B7280")
    
    def __repr__(self) -> str:
        """Строковое представление проекта."""
        return f"<Portfolio(title={self.title}, client={self.client})>" 