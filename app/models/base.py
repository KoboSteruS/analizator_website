"""
Базовая модель для всех моделей приложения.
Содержит общие поля: id (UUID), created_at, updated_at.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from app import db


class BaseModel(db.Model):
    """
    Базовая модель для всех моделей приложения.
    
    Содержит:
    - id: UUID первичный ключ
    - created_at: Дата создания записи
    - updated_at: Дата последнего обновления записи
    """
    
    __abstract__ = True
    
    # UUID первичный ключ
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Уникальный идентификатор записи"
    )
    
    # Дата создания
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Дата и время создания записи"
    )
    
    # Дата обновления
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Дата и время последнего обновления записи"
    )
    
    @declared_attr
    def __tablename__(cls):
        """Автоматическое именование таблиц в snake_case."""
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def to_dict(self) -> dict:
        """
        Преобразование модели в словарь.
        
        Returns:
            dict: Словарь с данными модели
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Преобразование UUID и datetime в строки
            if isinstance(value, uuid.UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        return result
    
    def update(self, **kwargs) -> None:
        """
        Обновление полей модели.
        
        Args:
            **kwargs: Поля для обновления
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
    
    def save(self) -> 'BaseModel':
        """
        Сохранение модели в базе данных.
        
        Returns:
            BaseModel: Сохраненная модель
        """
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self) -> None:
        """Удаление модели из базы данных."""
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self) -> str:
        """Строковое представление модели."""
        return f"<{self.__class__.__name__}(id={self.id})>" 