"""
Модуль для обработки загрузки изображений.
Содержит функции для валидации, загрузки и оптимизации изображений.
"""

import os
import uuid
from typing import Tuple, Optional, List
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from loguru import logger
import mimetypes

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# MIME типы изображений
ALLOWED_MIME_TYPES = {
    'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'
}

# Максимальный размер файла в байтах (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Максимальные размеры изображения
MAX_IMAGE_WIDTH = 1920
MAX_IMAGE_HEIGHT = 1080

# Размеры для превью
THUMBNAIL_SIZE = (300, 300)


def validate_image_file(file: FileStorage) -> Tuple[bool, str]:
    """
    Валидация загруженного файла изображения.
    
    Args:
        file: Загруженный файл
        
    Returns:
        Tuple[bool, str]: (валидность, сообщение об ошибке)
    """
    try:
        # Проверка наличия файла
        if not file or not file.filename:
            return False, "Файл не выбран"
        
        # Проверка расширения файла
        filename = secure_filename(file.filename.lower())
        if '.' not in filename:
            return False, "Файл должен иметь расширение"
        
        ext = filename.rsplit('.', 1)[1]
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Разрешены только файлы: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Проверка MIME типа
        mime_type = file.mimetype
        if mime_type not in ALLOWED_MIME_TYPES:
            return False, "Неподдерживаемый тип файла"
        
        # Проверка размера файла
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return False, f"Размер файла не должен превышать {MAX_FILE_SIZE // (1024 * 1024)}MB"
        
        # Проверка валидности изображения через PIL
        try:
            with Image.open(file.stream) as img:
                img.verify()
            file.seek(0)  # Сброс позиции файла после verify()
        except Exception as e:
            logger.warning(f"Ошибка валидации изображения: {e}")
            return False, "Поврежденный или некорректный файл изображения"
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Ошибка валидации файла: {e}")
        return False, "Ошибка обработки файла"


def get_upload_path(category: str) -> str:
    """
    Получение пути для загрузки файлов.
    
    Args:
        category: Категория файлов ('portfolio' или 'services')
        
    Returns:
        str: Абсолютный путь к папке загрузки
    """
    from flask import current_app
    
    upload_dir = os.path.join(current_app.static_folder, 'uploads', category)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def optimize_image(image_path: str, max_width: int = MAX_IMAGE_WIDTH, 
                  max_height: int = MAX_IMAGE_HEIGHT, quality: int = 85) -> bool:
    """
    Оптимизация изображения: изменение размера и качества.
    
    Args:
        image_path: Путь к изображению
        max_width: Максимальная ширина
        max_height: Максимальная высота
        quality: Качество сжатия (1-100)
        
    Returns:
        bool: Успешность операции
    """
    try:
        with Image.open(image_path) as img:
            # Конвертация RGBA в RGB для JPEG
            if img.mode == 'RGBA' and image_path.lower().endswith(('.jpg', '.jpeg')):
                # Создаем белый фон
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if len(img.split()) == 4 else None)
                img = background
            
            # Поворот по EXIF данным
            img = ImageOps.exif_transpose(img)
            
            # Изменение размера с сохранением пропорций
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Сохранение с оптимизацией
            save_kwargs = {'optimize': True}
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['quality'] = quality
                save_kwargs['format'] = 'JPEG'
            elif image_path.lower().endswith('.png'):
                save_kwargs['format'] = 'PNG'
            
            img.save(image_path, **save_kwargs)
            
        logger.info(f"Изображение оптимизировано: {image_path}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка оптимизации изображения {image_path}: {e}")
        return False


def create_thumbnail(image_path: str, thumbnail_path: str) -> bool:
    """
    Создание превью изображения.
    
    Args:
        image_path: Путь к исходному изображению
        thumbnail_path: Путь для сохранения превью
        
    Returns:
        bool: Успешность операции
    """
    try:
        with Image.open(image_path) as img:
            # Конвертация RGBA в RGB для JPEG
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if len(img.split()) == 4 else None)
                img = background
            
            # Поворот по EXIF данным
            img = ImageOps.exif_transpose(img)
            
            # Создание квадратного превью с центрированием
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            # Создание квадратного превью
            thumb_size = min(img.size)
            left = (img.width - thumb_size) // 2
            top = (img.height - thumb_size) // 2
            right = left + thumb_size
            bottom = top + thumb_size
            
            img = img.crop((left, top, right, bottom))
            img = img.resize(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            # Сохранение превью
            img.save(thumbnail_path, 'JPEG', quality=80, optimize=True)
            
        logger.info(f"Превью создано: {thumbnail_path}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка создания превью {thumbnail_path}: {e}")
        return False


def upload_image(file: FileStorage, category: str, 
                create_thumb: bool = True) -> Tuple[bool, str, Optional[str]]:
    """
    Загрузка и обработка изображения.
    
    Args:
        file: Загруженный файл
        category: Категория ('portfolio' или 'services')
        create_thumb: Создавать ли превью
        
    Returns:
        Tuple[bool, str, Optional[str]]: (успешность, путь/ошибка, путь к превью)
    """
    try:
        # Валидация файла
        is_valid, error_msg = validate_image_file(file)
        if not is_valid:
            return False, error_msg, None
        
        # Генерация уникального имени файла
        filename = secure_filename(file.filename.lower())
        ext = filename.rsplit('.', 1)[1]
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Получение пути для загрузки
        upload_dir = get_upload_path(category)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Сохранение файла
        file.save(file_path)
        logger.info(f"Файл сохранен: {file_path}")
        
        # Оптимизация изображения
        if not optimize_image(file_path):
            logger.warning(f"Не удалось оптимизировать изображение: {file_path}")
        
        # Создание превью
        thumbnail_path = None
        if create_thumb:
            thumb_filename = f"thumb_{unique_filename}"
            thumbnail_path = os.path.join(upload_dir, thumb_filename)
            
            if not create_thumbnail(file_path, thumbnail_path):
                logger.warning(f"Не удалось создать превью: {thumbnail_path}")
                thumbnail_path = None
        
        # Возвращаем относительный путь для URL
        relative_path = f"/static/uploads/{category}/{unique_filename}"
        thumb_relative_path = f"/static/uploads/{category}/thumb_{unique_filename}" if thumbnail_path else None
        
        logger.info(f"Изображение успешно загружено: {relative_path}")
        return True, relative_path, thumb_relative_path
        
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {e}")
        return False, f"Ошибка загрузки: {str(e)}", None


def delete_image(image_path: str) -> bool:
    """
    Удаление изображения и его превью.
    
    Args:
        image_path: Относительный путь к изображению
        
    Returns:
        bool: Успешность операции
    """
    try:
        from flask import current_app
        
        if not image_path or not image_path.startswith('/static/uploads/'):
            return True  # Нечего удалять
        
        # Получение абсолютного пути
        relative_path = image_path.replace('/static/', '')
        full_path = os.path.join(current_app.static_folder, relative_path)
        
        # Удаление основного файла
        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"Изображение удалено: {full_path}")
        
        # Удаление превью
        dir_path = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        thumb_path = os.path.join(dir_path, f"thumb_{filename}")
        
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
            logger.info(f"Превью удалено: {thumb_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка удаления изображения {image_path}: {e}")
        return False


def get_image_info(image_path: str) -> Optional[dict]:
    """
    Получение информации об изображении.
    
    Args:
        image_path: Путь к изображению
        
    Returns:
        dict: Информация об изображении или None
    """
    try:
        from flask import current_app
        
        if not image_path or not image_path.startswith('/static/uploads/'):
            return None
        
        relative_path = image_path.replace('/static/', '')
        full_path = os.path.join(current_app.static_folder, relative_path)
        
        if not os.path.exists(full_path):
            return None
        
        # Получение размера файла
        file_size = os.path.getsize(full_path)
        
        # Получение размеров изображения
        with Image.open(full_path) as img:
            width, height = img.size
            format_name = img.format
        
        return {
            'path': image_path,
            'size': file_size,
            'width': width,
            'height': height,
            'format': format_name,
            'size_mb': round(file_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения информации об изображении {image_path}: {e}")
        return None 