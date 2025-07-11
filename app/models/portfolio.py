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
        WEB_DEVELOPMENT = "Веб-разработка"
        MOBILE_APP = "Мобильное приложение"
        DIGITAL_MARKETING = "Цифровой маркетинг"
        BRANDING = "Брендинг"
        DESIGN = "Дизайн"
        ECOMMERCE = "E-commerce"
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
                'title': 'Loka Perfume & Co.',
                'description': 'Интернет-магазин премиальной парфюмерии с современным дизайном и удобной навигацией.',
                'client': 'Loka Perfume & Co.',
                'location': 'Москва',
                'category': cls.Category.WEB_DEVELOPMENT,
                'price': 150000,
                'completion_date': datetime(2024, 1, 18),
                'is_featured': True,
                'sort_order': 6,
                'status': cls.Status.COMPLETED
            },
            {
                'title': 'Compass Shoes',
                'description': 'Маркетинговая кампания для продвижения обувного бренда в социальных сетях.',
                'client': 'Compass Shoes',
                'location': 'Санкт-Петербург',
                'category': cls.Category.DIGITAL_MARKETING,
                'price': 75000,
                'completion_date': datetime(2024, 1, 15),
                'is_featured': False,
                'sort_order': 5,
                'status': cls.Status.COMPLETED
            },
            {
                'title': 'Digital Dynamics',
                'description': 'Веб-приложение для управления цифровыми активами компании с аналитикой.',
                'client': 'Digital Dynamics',
                'location': 'Москва',
                'category': cls.Category.WEB_DEVELOPMENT,
                'price': 250000,
                'completion_date': datetime(2024, 1, 12),
                'is_featured': True,
                'sort_order': 4,
                'status': cls.Status.COMPLETED
            },
            {
                'title': 'Fresh Bites Catering',
                'description': 'Разработка фирменного стиля и брендинга для кейтеринговой компании.',
                'client': 'Fresh Bites Catering',
                'location': 'Москва',
                'category': cls.Category.BRANDING,
                'price': 85000,
                'completion_date': datetime(2024, 1, 10),
                'is_featured': False,
                'sort_order': 3,
                'status': cls.Status.COMPLETED
            },
            {
                'title': 'Harmony Spa & Wellness',
                'description': 'Сайт-визитка для спа-салона с онлайн записью и каталогом услуг.',
                'client': 'Harmony Spa & Wellness',
                'location': 'Москва',
                'category': cls.Category.WEB_DEVELOPMENT,
                'price': 120000,
                'completion_date': datetime(2024, 1, 8),
                'is_featured': False,
                'sort_order': 2,
                'status': cls.Status.COMPLETED
            },
            {
                'title': 'LuxJewelry Collection',
                'description': 'E-commerce платформа для продажи эксклюзивных ювелирных изделий.',
                'client': 'LuxJewelry Collection',
                'location': 'Москва',
                'category': cls.Category.ECOMMERCE,
                'price': 200000,
                'completion_date': datetime(2024, 1, 5),
                'is_featured': True,
                'sort_order': 1,
                'status': cls.Status.COMPLETED
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
    
    def get_category_color(self) -> str:
        """
        Получение цвета для категории.
        
        Returns:
            str: HEX цвет для категории
        """
        colors = {
            self.Category.WEB_DEVELOPMENT: "#8B5CF6",
            self.Category.MOBILE_APP: "#EC4899",
            self.Category.DIGITAL_MARKETING: "#F472B6",
            self.Category.BRANDING: "#F59E0B",
            self.Category.DESIGN: "#10B981",
            self.Category.ECOMMERCE: "#EF4444",
            self.Category.OTHER: "#6B7280"
        }
        return colors.get(self.category, "#6B7280")
    
    def __repr__(self) -> str:
        """Строковое представление проекта."""
        return f"<Portfolio(title={self.title}, client={self.client})>" 