"""
Модель услуг для админки.
Содержит информацию об услугах компании.
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, Float
from app.models.base import BaseModel


class Service(BaseModel):
    """
    Модель услуги.
    
    Поля:
    - title: Название услуги
    - description: Описание услуги
    - icon: CSS класс иконки (Font Awesome)
    - is_active: Флаг активности услуги
    - sort_order: Порядок сортировки
    - color: Цвет акцента для иконки (hex)
    - price_from: Цена от (опционально)
    - duration: Длительность выполнения
    - features: Список особенностей (JSON строка)
    """
    
    __tablename__ = 'services'
    
    title = Column(
        String(200),
        nullable=False,
        comment="Название услуги"
    )
    
    description = Column(
        Text,
        nullable=False,
        comment="Описание услуги"
    )
    
    icon = Column(
        String(100),
        nullable=False,
        default="fas fa-cog",
        comment="CSS класс иконки Font Awesome"
    )
    
    # Временно отключено для исправления проблем на продакшн
    # image_url = Column(
    #     String(500),
    #     nullable=True,
    #     comment="URL изображения услуги (альтернатива иконке)"
    # )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Флаг активности услуги"
    )
    
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Порядок сортировки"
    )
    
    color = Column(
        String(7),
        default="#8B5CF6",
        nullable=False,
        comment="Цвет акцента (hex)"
    )
    
    price_from = Column(
        Float,
        nullable=True,
        comment="Цена от (в рублях)"
    )
    
    duration = Column(
        String(100),
        nullable=True,
        comment="Длительность выполнения"
    )
    
    features = Column(
        Text,
        nullable=True,
        comment="Список особенностей (JSON)"
    )
    
    @classmethod
    def get_active(cls):
        """
        Получение всех активных услуг с сортировкой.
        
        Returns:
            List[Service]: Список активных услуг
        """
        return cls.query.filter_by(is_active=True).order_by(cls.sort_order).all()
    
    @classmethod
    def create_default_services(cls):
        """Создание услуг по умолчанию."""
        default_services = [
            {
                'title': 'Веб-разработка',
                'description': 'Создание современных веб-приложений и сайтов с использованием последних технологий.',
                'icon': 'fas fa-globe',
                'sort_order': 1,
                'color': '#8B5CF6',
                'price_from': 50000,
                'duration': '2-4 недели'
            },
            {
                'title': 'Разработка приложений',
                'description': 'Мобильные и десктопные приложения для iOS, Android и Windows.',
                'icon': 'fas fa-mobile-alt',
                'sort_order': 2,
                'color': '#EC4899',
                'price_from': 100000,
                'duration': '4-8 недель'
            },
            {
                'title': 'Анализ кредитных заявок',
                'description': 'ИИ-система для автоматического анализа и скоринга кредитных заявок.',
                'icon': 'fas fa-chart-line',
                'sort_order': 3,
                'color': '#F472B6',
                'price_from': 200000,
                'duration': '6-12 недель'
            },
            {
                'title': 'Графический дизайн',
                'description': 'Создание брендинга, логотипов, UI/UX дизайна и графических материалов.',
                'icon': 'fas fa-paint-brush',
                'sort_order': 4,
                'color': '#10B981',
                'price_from': 25000,
                'duration': '1-2 недели'
            },
            {
                'title': 'Брендинг',
                'description': 'Разработка фирменного стиля, создание бренд-бука и маркетинговых материалов.',
                'icon': 'fas fa-layer-group',
                'sort_order': 5,
                'color': '#F59E0B',
                'price_from': 75000,
                'duration': '3-5 недель'
            },
            {
                'title': 'SEO оптимизация',
                'description': 'Комплексная оптимизация сайта для поисковых систем и увеличения трафика.',
                'icon': 'fas fa-search',
                'sort_order': 6,
                'color': '#EF4444',
                'price_from': 30000,
                'duration': '1-3 месяца'
            }
        ]
        
        created_services = []
        for service_data in default_services:
            # Проверяем, не существует ли уже такая услуга
            existing = cls.query.filter_by(title=service_data['title']).first()
            if not existing:
                service = cls(**service_data)
                created_services.append(service)
        
        return created_services
    
    def to_dict(self) -> dict:
        """
        Преобразование в словарь.
        
        Returns:
            dict: Данные услуги
        """
        data = super().to_dict()
        
        # Парсим JSON особенности если есть
        if self.features:
            try:
                import json
                data['features_list'] = json.loads(self.features)
            except:
                data['features_list'] = []
        else:
            data['features_list'] = []
        
        return data
    
    def set_features(self, features_list: list) -> None:
        """
        Установка списка особенностей.
        
        Args:
            features_list: Список особенностей
        """
        import json
        self.features = json.dumps(features_list, ensure_ascii=False)
    
    def __repr__(self) -> str:
        """Строковое представление услуги."""
        return f"<Service(title={self.title}, active={self.is_active})>" 