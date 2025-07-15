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
    
    image_url = Column(
        String(500),
        nullable=True,
        comment="URL изображения услуги (альтернатива иконке)"
    )
    
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
                'title': 'Разработка ботов',
                'description': 'Создание автоматизированных ботов для Telegram, WhatsApp и других мессенджеров. Интеграция с маркетплейсами и CRM системами.',
                'icon': 'fas fa-robot',
                'sort_order': 1,
                'color': '#8B5CF6',
                'price_from': 25000,
                'duration': '1-2 недели',
                'features': '["Интеграция с API маркетплейсов", "Автоответчик клиентам", "Уведомления о заказах", "Статистика продаж"]'
            },
            {
                'title': 'Создание лендинга',
                'description': 'Разработка продающих лендинг-страниц для товаров и услуг. Адаптивная верстка, SEO оптимизация и интеграция с аналитикой.',
                'icon': 'fas fa-palette',
                'sort_order': 2,
                'color': '#EC4899',
                'price_from': 15000,
                'duration': '3-5 дней',
                'features': '["Адаптивный дизайн", "SEO оптимизация", "Интеграция с Google Analytics", "Форма обратной связи"]'
            },
            {
                'title': 'Внедрение ИИ в компанию',
                'description': 'Консультации и внедрение искусственного интеллекта в бизнес-процессы. Автоматизация рутинных задач с помощью AI.',
                'icon': 'fas fa-brain',
                'sort_order': 3,
                'color': '#F472B6',
                'price_from': 100000,
                'duration': '2-4 месяца',
                'features': '["Анализ бизнес-процессов", "Подбор AI решений", "Внедрение и настройка", "Обучение персонала"]'
            },
            {
                'title': 'Внедрение системы учета',
                'description': 'Настройка и внедрение систем управленческого и бухгалтерского учета. Интеграция с маркетплейсами и банками.',
                'icon': 'fas fa-calculator',
                'sort_order': 4,
                'color': '#10B981',
                'price_from': 50000,
                'duration': '2-6 недель',
                'features': '["Настройка 1С", "Интеграция с маркетплейсами", "Автоматизация отчетности", "Обучение пользователей"]'
            },
            {
                'title': 'Аудит и автоматизация бизнес-процессов',
                'description': 'Комплексный анализ бизнес-процессов компании и разработка решений для их автоматизации и оптимизации.',
                'icon': 'fas fa-tasks',
                'sort_order': 5,
                'color': '#F59E0B',
                'price_from': 75000,
                'duration': '1-2 месяца',
                'features': '["Анализ текущих процессов", "Выявление узких мест", "Разработка рекомендаций", "Внедрение автоматизации"]'
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
        
        # Форматируем цену
        if self.price_from:
            data['price_formatted'] = f"от ₽{self.price_from:,.0f}".replace(',', ' ')
        else:
            data['price_formatted'] = "По запросу"
        
        return data
    
    def set_features(self, features_list: list) -> None:
        """
        Установка списка особенностей.
        
        Args:
            features_list: Список особенностей
        """
        import json
        self.features = json.dumps(features_list, ensure_ascii=False)
    
    def get_features(self) -> list:
        """
        Получение списка особенностей.
        
        Returns:
            list: Список особенностей услуги
        """
        if not self.features:
            return []
        
        try:
            import json
            return json.loads(self.features)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def __repr__(self) -> str:
        """Строковое представление услуги."""
        return f"<Service(title={self.title}, active={self.is_active})>" 