"""
Модель пользователя для админки.
Содержит поля для авторизации и JWT токенов.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Boolean, DateTime, Text
from datetime import datetime, timedelta
from app.models.base import BaseModel
from app import db
import secrets


class User(BaseModel):
    """
    Модель пользователя.
    
    Поля:
    - email: Email пользователя (уникальный)
    - password_hash: Хэш пароля
    - is_superuser: Флаг суперпользователя
    - is_active: Флаг активного пользователя
    - jwt_secret: Персональный JWT секрет для доступа к админке
    - last_login: Дата последнего входа
    - full_name: Полное имя
    """
    
    __tablename__ = 'users'
    
    email = Column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
        comment="Email пользователя"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Хэш пароля"
    )
    
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Флаг суперпользователя"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Флаг активного пользователя"
    )
    
    jwt_secret = Column(
        String(64),
        unique=True,
        nullable=False,
        comment="Персональный JWT секрет для админки"
    )
    
    last_login = Column(
        DateTime,
        nullable=True,
        comment="Дата последнего входа"
    )
    
    full_name = Column(
        String(200),
        nullable=True,
        comment="Полное имя пользователя"
    )
    
    def __init__(self, **kwargs):
        """Инициализация пользователя с генерацией JWT секрета."""
        if 'jwt_secret' not in kwargs:
            kwargs['jwt_secret'] = self.generate_jwt_secret()
        super().__init__(**kwargs)
    
    def set_password(self, password: str) -> None:
        """
        Установка пароля пользователя.
        
        Args:
            password: Пароль в открытом виде
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Проверка пароля пользователя.
        
        Args:
            password: Пароль в открытом виде
            
        Returns:
            bool: True если пароль корректный
        """
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generate_jwt_secret() -> str:
        """
        Генерация уникального JWT секрета.
        
        Returns:
            str: Случайный секрет длиной 64 символа
        """
        return secrets.token_urlsafe(48)
    
    def regenerate_jwt_secret(self) -> str:
        """
        Перегенерация JWT секрета.
        
        Returns:
            str: Новый JWT секрет
        """
        self.jwt_secret = self.generate_jwt_secret()
        return self.jwt_secret
    
    def update_last_login(self) -> None:
        """Обновление времени последнего входа."""
        self.last_login = datetime.utcnow()
    
    @classmethod
    def create_superuser(
        cls, 
        email: str, 
        password: str, 
        full_name: str = None
    ) -> 'User':
        """
        Создание суперпользователя.
        
        Args:
            email: Email суперпользователя
            password: Пароль
            full_name: Полное имя (опционально)
            
        Returns:
            User: Созданный суперпользователь
        """
        # Проверяем, не существует ли уже пользователь с таким email
        existing_user = cls.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError(f"Пользователь с email {email} уже существует")
        
        user = cls(
            email=email,
            is_superuser=True,
            is_active=True,
            full_name=full_name or "Администратор"
        )
        user.set_password(password)
        
        return user
    
    @classmethod
    def get_by_jwt_secret(cls, jwt_secret: str) -> 'User':
        """
        Получение пользователя по JWT секрету.
        
        Args:
            jwt_secret: JWT секрет
            
        Returns:
            User: Пользователь или None
        """
        return cls.query.filter_by(
            jwt_secret=jwt_secret,
            is_active=True
        ).first()
    
    def to_dict(self) -> dict:
        """
        Преобразование в словарь (без конфиденциальной информации).
        
        Returns:
            dict: Данные пользователя
        """
        data = super().to_dict()
        # Удаляем конфиденциальные поля
        data.pop('password_hash', None)
        return data
    
    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User(email={self.email}, is_superuser={self.is_superuser})>" 