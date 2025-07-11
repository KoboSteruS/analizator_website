"""
Основные роуты приложения.
Содержит все основные страницы веб-сайта.
"""

from flask import Blueprint, render_template, jsonify, request
from loguru import logger
from datetime import datetime
from app.models import Service, Portfolio

# Создание blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def homepage():
    """Главная страница."""
    logger.info("Запрос к главной странице")
    
    # Получаем данные для главной страницы
    featured_services = Service.query.filter_by(is_active=True).order_by(Service.sort_order).limit(6).all()
    featured_projects = Portfolio.get_featured()[:3]  # Только 3 избранных проекта
    
    return render_template('index.html', 
                         services=featured_services,
                         featured_projects=featured_projects)


@main_bp.route('/api/', methods=['GET'])
def api_index():
    """
    API эндпоинт главной страницы.
    
    Returns:
        dict: Информация о приложении
    """
    logger.info("Запрос к API главной страницы")
    
    return jsonify({
        "message": "Анализатор кредитных заявок",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs"
        }
    }), 200


@main_bp.route('/about', methods=['GET'])
def about():
    """Страница "О нас"."""
    logger.info("Запрос к странице 'О нас'")
    return render_template('about.html')


@main_bp.route('/services', methods=['GET'])
def services():
    """Страница услуг."""
    logger.info("Запрос к странице услуг")
    
    # Получаем все активные услуги
    services_list = Service.get_active()
    
    return render_template('services.html', services=services_list)


@main_bp.route('/portfolio', methods=['GET'])
def portfolio():
    """Страница портфолио."""
    logger.info("Запрос к странице портфолио")
    
    # Получаем все активные проекты
    portfolio_list = Portfolio.get_active()
    
    return render_template('portfolio.html', portfolio=portfolio_list)


@main_bp.route('/pricing', methods=['GET'])
def pricing():
    """Страница тарифов."""
    logger.info("Запрос к странице тарифов")
    return render_template('pricing.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Страница контактов."""
    if request.method == 'POST':
        logger.info("Получена контактная форма")
        # Здесь будет обработка формы
        return jsonify({"status": "success", "message": "Сообщение отправлено"})
    
    logger.info("Запрос к странице контактов")
    return render_template('contact.html')


@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Проверка состояния приложения.
    
    Returns:
        dict: Статус работы приложения
    """
    logger.info("Проверка здоровья приложения")
    
    try:
        # Здесь можно добавить проверки БД, внешних сервисов и т.д.
        from app import db
        
        # Простая проверка подключения к БД
        db.engine.execute('SELECT 1')
        db_status = "connected"
        
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        db_status = "disconnected"
    
    health_data = {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "api": "active"
        },
        "uptime": "OK"
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    
    return jsonify(health_data), status_code


@main_bp.route('/docs', methods=['GET'])
def api_docs():
    """
    Документация API.
    
    Returns:
        dict: Список доступных endpoints
    """
    logger.info("Запрос документации API")
    
    return jsonify({
        "title": "Анализатор кредитных заявок API",
        "version": "1.0.0",
        "description": "API для анализа и обработки кредитных заявок",
        "endpoints": {
            "GET /": "Главная страница API",
            "GET /health": "Проверка состояния приложения",
            "GET /docs": "Документация API"
        },
        "authentication": "JWT Bearer Token (будет добавлено)",
        "content_type": "application/json"
    }), 200


@main_bp.errorhandler(404)
def not_found_in_main(error):
    """Обработчик 404 ошибки для основного blueprint."""
    logger.warning(f"404 в основном blueprint: {request.url}")
    
    return jsonify({
        "error": "Endpoint не найден",
        "message": f"Запрошенный путь '{request.path}' не существует",
        "available_endpoints": ["/", "/health", "/docs"]
    }), 404


@main_bp.before_request
def log_request():
    """Логирование всех запросов к основному blueprint."""
    logger.info(f"{request.method} {request.path} от {request.remote_addr}")


@main_bp.after_request
def log_response(response):
    """Логирование ответов основного blueprint."""
    logger.info(f"Ответ {response.status_code} для {request.method} {request.path}")
    return response 