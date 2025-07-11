"""
Роуты приложения.
Содержит все blueprints и API endpoints.
"""

from .main import main_bp

# Здесь будут импорты всех blueprints при их создании
# from .auth import auth_bp
# from .api import api_bp

__all__ = [
    'main_bp',
    # Добавлять новые blueprints в этот список
] 