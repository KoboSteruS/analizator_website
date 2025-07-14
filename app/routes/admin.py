"""
Роуты админки.
Содержит все роуты для управления контентом через JWT авторизацию.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from loguru import logger
from datetime import datetime
import uuid

from app import db
from app.models import User, Service, Portfolio
from app.utils import upload_image, delete_image, get_image_info, log_security_event, log_admin_action


def create_admin_blueprint(jwt_secret: str) -> Blueprint:
    """
    Создание blueprint для админки с определенным JWT секретом.
    
    Args:
        jwt_secret: JWT секрет для доступа к админке
        
    Returns:
        Blueprint: Настроенный blueprint админки
    """
    admin_bp = Blueprint(f'admin_{jwt_secret}', __name__, url_prefix=f'/{jwt_secret}/admin')
    
    def admin_required(f):
        """Декоратор для проверки доступа к админке."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Проверяем JWT секрет в URL
            user = User.get_by_jwt_secret(jwt_secret)
            if not user or not user.is_superuser:
                logger.warning(f"Неавторизованный доступ к админке с JWT: {jwt_secret}")
                log_security_event(
                    event_type="ADMIN_ACCESS_DENIED",
                    details={
                        'jwt_secret': jwt_secret[:10] + "...",  # Частичное логирование JWT
                        'reason': 'invalid_jwt_or_not_superuser'
                    }
                )
                return jsonify({"error": "Доступ запрещен"}), 403
            
            # Успешный доступ к админке
            log_security_event(
                event_type="ADMIN_ACCESS_GRANTED",
                user_id=str(user.id),
                details={'email': user.email}
            )
            
            # Сохраняем пользователя в сессии
            session['admin_user_id'] = str(user.id)
            return f(*args, **kwargs)
        return decorated_function
    
    @admin_bp.route('/', strict_slashes=False)
    @admin_required
    def dashboard():
        """Главная страница админки."""
        user = User.get_by_jwt_secret(jwt_secret)
        user.update_last_login()
        db.session.commit()
        
        # Статистика
        stats = {
            'services_count': Service.query.filter_by(is_active=True).count(),
            'portfolio_count': Portfolio.query.filter_by(is_active=True).count(),
            'featured_projects': Portfolio.query.filter_by(is_featured=True).count(),
            'total_projects_value': db.session.query(db.func.sum(Portfolio.price)).filter_by(is_active=True).scalar() or 0
        }
        
        logger.info(f"Администратор {user.email} зашел в админку")
        return render_template('admin/dashboard.html', user=user, stats=stats, jwt_secret=jwt_secret)
    
    # ===== SERVICES ROUTES =====
    
    @admin_bp.route('/services', strict_slashes=False)
    @admin_required
    def services():
        """Страница управления услугами."""
        user = User.get_by_jwt_secret(jwt_secret)
        services_list = Service.query.order_by(Service.sort_order).all()
        return render_template('admin/services.html', user=user, services=services_list, jwt_secret=jwt_secret)
    
    @admin_bp.route('/services/new', methods=['GET', 'POST'])
    @admin_required
    def service_new():
        """Создание новой услуги."""
        if request.method == 'POST':
            try:
                # Обработка загрузки изображения
                image_url = None
                upload_error = None
                
                if 'image_file' in request.files and request.files['image_file'].filename:
                    # Загрузка нового изображения
                    file = request.files['image_file']
                    success, result, thumb_path = upload_image(file, 'services')
                    if success:
                        image_url = result
                        logger.info(f"Изображение загружено для услуги: {image_url}")
                    else:
                        upload_error = result
                        logger.error(f"Ошибка загрузки изображения: {upload_error}")
                elif request.form.get('image_url'):
                    # Использование URL изображения
                    image_url = request.form.get('image_url')
                
                service = Service(
                    title=request.form['title'],
                    description=request.form['description'],
                    icon=request.form.get('icon', 'fas fa-cog'),
                    image_url=image_url,
                    color=request.form.get('color', '#8B5CF6'),
                    price_from=float(request.form['price_from']) if request.form.get('price_from') else None,
                    duration=request.form.get('duration'),
                    sort_order=int(request.form.get('sort_order', 0)),
                    is_active=bool(request.form.get('is_active'))
                )
                
                # Обработка особенностей
                features = []
                for i in range(10):  # Максимум 10 особенностей
                    feature = request.form.get(f'feature_{i}')
                    if feature and feature.strip():
                        features.append(feature.strip())
                
                if features:
                    service.set_features(features)
                
                # Проверка ошибок загрузки изображения
                if upload_error:
                    user = User.get_by_jwt_secret(jwt_secret)
                    return render_template('admin/service_form.html', 
                                         user=user,
                                         error=f"Ошибка загрузки изображения: {upload_error}",
                                         jwt_secret=jwt_secret)
                
                db.session.add(service)
                db.session.commit()
                
                # Логирование действия админа
                user_id = session.get('admin_user_id')
                log_admin_action(
                    action="CREATE",
                    resource="service",
                    resource_id=str(service.id),
                    user_id=user_id,
                    details={
                        'title': service.title,
                        'price_from': service.price_from,
                        'has_image': bool(service.image_url)
                    }
                )
                
                logger.info(f"Создана новая услуга: {service.title}")
                return redirect(url_for(f'admin_{jwt_secret}.services'))
                
            except Exception as e:
                logger.error(f"Ошибка создания услуги: {e}")
                db.session.rollback()
                user = User.get_by_jwt_secret(jwt_secret)
                return render_template('admin/service_form.html', 
                                     user=user,
                                     error="Ошибка создания услуги", 
                                     jwt_secret=jwt_secret)
        
        user = User.get_by_jwt_secret(jwt_secret)
        return render_template('admin/service_form.html', user=user, jwt_secret=jwt_secret)
    
    @admin_bp.route('/services/<service_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def service_edit(service_id):
        """Редактирование услуги."""
        try:
            service_uuid = uuid.UUID(service_id)
        except ValueError:
            return jsonify({"error": "Неверный ID услуги"}), 400
        
        service = Service.query.get_or_404(service_uuid)
        
        if request.method == 'POST':
            try:
                # Обработка загрузки изображения
                upload_error = None
                old_image_url = service.image_url
                
                if 'image_file' in request.files and request.files['image_file'].filename:
                    # Загрузка нового изображения
                    file = request.files['image_file']
                    success, result, thumb_path = upload_image(file, 'services')
                    if success:
                        # Удаление старого изображения если оно было загружено через систему
                        if old_image_url and old_image_url.startswith('/static/uploads/'):
                            delete_image(old_image_url)
                        service.image_url = result
                        logger.info(f"Изображение обновлено для услуги: {service.image_url}")
                    else:
                        upload_error = result
                        logger.error(f"Ошибка загрузки изображения: {upload_error}")
                elif request.form.get('image_url') != old_image_url:
                    # Обновление URL изображения
                    if old_image_url and old_image_url.startswith('/static/uploads/'):
                        delete_image(old_image_url)
                    service.image_url = request.form.get('image_url')
                
                service.title = request.form['title']
                service.description = request.form['description']
                service.icon = request.form.get('icon', 'fas fa-cog')
                service.color = request.form.get('color', '#8B5CF6')
                service.price_from = float(request.form['price_from']) if request.form.get('price_from') else None
                service.duration = request.form.get('duration')
                service.sort_order = int(request.form.get('sort_order', 0))
                service.is_active = bool(request.form.get('is_active'))
                
                # Обработка особенностей
                features = []
                for i in range(10):  # Максимум 10 особенностей
                    feature = request.form.get(f'feature_{i}')
                    if feature and feature.strip():
                        features.append(feature.strip())
                
                service.set_features(features)
                
                # Проверка ошибок загрузки изображения
                if upload_error:
                    user = User.get_by_jwt_secret(jwt_secret)
                    return render_template('admin/service_form.html', 
                                         user=user,
                                         service=service,
                                         error=f"Ошибка загрузки изображения: {upload_error}",
                                         jwt_secret=jwt_secret)
                
                db.session.commit()
                
                # Логирование действия админа
                user_id = session.get('admin_user_id')
                log_admin_action(
                    action="UPDATE",
                    resource="service",
                    resource_id=str(service.id),
                    user_id=user_id,
                    details={
                        'title': service.title,
                        'price_from': service.price_from,
                        'has_image': bool(service.image_url),
                        'image_updated': bool(upload_error is None and 'image_file' in request.files)
                    }
                )
                
                logger.info(f"Обновлена услуга: {service.title}")
                return redirect(url_for(f'admin_{jwt_secret}.services'))
                
            except Exception as e:
                logger.error(f"Ошибка обновления услуги: {e}")
                db.session.rollback()
                user = User.get_by_jwt_secret(jwt_secret)
                return render_template('admin/service_form.html', 
                                     user=user,
                                     service=service, 
                                     error="Ошибка обновления услуги",
                                     jwt_secret=jwt_secret)
        
        user = User.get_by_jwt_secret(jwt_secret)
        return render_template('admin/service_form.html', user=user, service=service, jwt_secret=jwt_secret)
    
    @admin_bp.route('/services/<service_id>/delete', methods=['POST'])
    @admin_required
    def service_delete(service_id):
        """Удаление услуги."""
        try:
            service_uuid = uuid.UUID(service_id)
        except ValueError:
            return jsonify({"error": "Неверный ID услуги"}), 400
        
        service = Service.query.get_or_404(service_uuid)
        
        try:
            title = service.title
            
            # Логирование действия админа
            user_id = session.get('admin_user_id')
            log_admin_action(
                action="DELETE",
                resource="service",
                resource_id=str(service.id),
                user_id=user_id,
                details={
                    'title': title,
                    'had_image': bool(service.image_url)
                }
            )
            
            db.session.delete(service)
            db.session.commit()
            
            logger.info(f"Удалена услуга: {title}")
            return jsonify({"success": True, "message": "Услуга удалена"})
            
        except Exception as e:
            logger.error(f"Ошибка удаления услуги: {e}")
            db.session.rollback()
            return jsonify({"success": False, "message": "Ошибка удаления услуги"}), 500
    
    # ===== PORTFOLIO ROUTES =====
    
    @admin_bp.route('/portfolio')
    @admin_required
    def portfolio():
        """Страница управления портфолио."""
        user = User.get_by_jwt_secret(jwt_secret)
        portfolio_list = Portfolio.query.order_by(Portfolio.sort_order.desc(), Portfolio.completion_date.desc()).all()
        return render_template('admin/portfolio.html', user=user, portfolio=portfolio_list, jwt_secret=jwt_secret)
    
    @admin_bp.route('/portfolio/new', methods=['GET', 'POST'])
    @admin_required
    def portfolio_new():
        """Создание нового проекта."""
        if request.method == 'POST':
            try:
                completion_date = None
                if request.form.get('completion_date'):
                    completion_date = datetime.strptime(request.form['completion_date'], '%Y-%m-%d')
                
                # Обработка загрузки изображения
                image_url = None
                upload_error = None
                
                if 'image_file' in request.files and request.files['image_file'].filename:
                    # Загрузка нового изображения
                    file = request.files['image_file']
                    success, result, thumb_path = upload_image(file, 'portfolio')
                    if success:
                        image_url = result
                        logger.info(f"Изображение загружено для проекта: {image_url}")
                    else:
                        upload_error = result
                        logger.error(f"Ошибка загрузки изображения: {upload_error}")
                elif request.form.get('image_url'):
                    # Использование URL изображения
                    image_url = request.form.get('image_url')
                
                project = Portfolio(
                    title=request.form['title'],
                    description=request.form['description'],
                    client=request.form['client'],
                    location=request.form.get('location'),
                    category=request.form['category'],
                    image_url=image_url,
                    project_url=request.form.get('project_url'),
                    price=float(request.form['price']) if request.form.get('price') else None,
                    completion_date=completion_date,
                    sort_order=int(request.form.get('sort_order', 0)),
                    is_featured=bool(request.form.get('is_featured')),
                    is_active=bool(request.form.get('is_active')),
                    status=request.form.get('status', Portfolio.Status.COMPLETED)
                )
                
                # Обработка технологий
                technologies = []
                for i in range(10):  # Максимум 10 технологий
                    tech = request.form.get(f'technology_{i}')
                    if tech and tech.strip():
                        technologies.append(tech.strip())
                
                if technologies:
                    project.set_technologies(technologies)
                
                # Проверка ошибок загрузки изображения
                if upload_error:
                    user = User.get_by_jwt_secret(jwt_secret)
                    return render_template('admin/portfolio_form.html', 
                                         user=user,
                                         error=f"Ошибка загрузки изображения: {upload_error}",
                                         categories=Portfolio.Category.__dict__,
                                         statuses=Portfolio.Status.__dict__,
                                         jwt_secret=jwt_secret)
                
                db.session.add(project)
                db.session.commit()
                
                # Логирование действия админа
                user_id = session.get('admin_user_id')
                log_admin_action(
                    action="CREATE",
                    resource="portfolio",
                    resource_id=str(project.id),
                    user_id=user_id,
                    details={
                        'title': project.title,
                        'client': project.client,
                        'category': project.category,
                        'price': project.price,
                        'is_featured': project.is_featured,
                        'has_image': bool(project.image_url)
                    }
                )
                
                logger.info(f"Создан новый проект: {project.title}")
                return redirect(url_for(f'admin_{jwt_secret}.portfolio'))
                
            except Exception as e:
                logger.error(f"Ошибка создания проекта: {e}")
                db.session.rollback()
                user = User.get_by_jwt_secret(jwt_secret)
                return render_template('admin/portfolio_form.html', 
                                     user=user,
                                     error="Ошибка создания проекта",
                                     categories=Portfolio.Category.__dict__,
                                     statuses=Portfolio.Status.__dict__,
                                     jwt_secret=jwt_secret)
        
        user = User.get_by_jwt_secret(jwt_secret)
        return render_template('admin/portfolio_form.html', 
                             user=user,
                             categories=Portfolio.Category.__dict__,
                             statuses=Portfolio.Status.__dict__,
                             jwt_secret=jwt_secret)
    
    @admin_bp.route('/portfolio/<project_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def portfolio_edit(project_id):
        """Редактирование проекта."""
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            return jsonify({"error": "Неверный ID проекта"}), 400
        
        project = Portfolio.query.get_or_404(project_uuid)
        
        if request.method == 'POST':
            try:
                completion_date = None
                if request.form.get('completion_date'):
                    completion_date = datetime.strptime(request.form['completion_date'], '%Y-%m-%d')
                
                # Обработка загрузки изображения
                upload_error = None
                old_image_url = project.image_url
                
                if 'image_file' in request.files and request.files['image_file'].filename:
                    # Загрузка нового изображения
                    file = request.files['image_file']
                    success, result, thumb_path = upload_image(file, 'portfolio')
                    if success:
                        # Удаление старого изображения если оно было загружено через систему
                        if old_image_url and old_image_url.startswith('/static/uploads/'):
                            delete_image(old_image_url)
                        project.image_url = result
                        logger.info(f"Изображение обновлено для проекта: {project.image_url}")
                    else:
                        upload_error = result
                        logger.error(f"Ошибка загрузки изображения: {upload_error}")
                elif request.form.get('image_url') != old_image_url:
                    # Обновление URL изображения
                    if old_image_url and old_image_url.startswith('/static/uploads/'):
                        delete_image(old_image_url)
                    project.image_url = request.form.get('image_url')
                
                project.title = request.form['title']
                project.description = request.form['description']
                project.client = request.form['client']
                project.location = request.form.get('location')
                project.category = request.form['category']
                project.project_url = request.form.get('project_url')
                project.price = float(request.form['price']) if request.form.get('price') else None
                project.completion_date = completion_date
                project.sort_order = int(request.form.get('sort_order', 0))
                project.is_featured = bool(request.form.get('is_featured'))
                project.is_active = bool(request.form.get('is_active'))
                project.status = request.form.get('status', Portfolio.Status.COMPLETED)
                
                # Обработка технологий
                technologies = []
                for i in range(10):  # Максимум 10 технологий
                    tech = request.form.get(f'technology_{i}')
                    if tech and tech.strip():
                        technologies.append(tech.strip())
                
                project.set_technologies(technologies)
                
                # Проверка ошибок загрузки изображения
                if upload_error:
                    user = User.get_by_jwt_secret(jwt_secret)
                    return render_template('admin/portfolio_form.html', 
                                         user=user,
                                         project=project,
                                         error=f"Ошибка загрузки изображения: {upload_error}",
                                         categories=Portfolio.Category.__dict__,
                                         statuses=Portfolio.Status.__dict__,
                                         jwt_secret=jwt_secret)
                
                db.session.commit()
                
                # Логирование действия админа
                user_id = session.get('admin_user_id')
                log_admin_action(
                    action="UPDATE",
                    resource="portfolio",
                    resource_id=str(project.id),
                    user_id=user_id,
                    details={
                        'title': project.title,
                        'client': project.client,
                        'category': project.category,
                        'price': project.price,
                        'is_featured': project.is_featured,
                        'has_image': bool(project.image_url),
                        'image_updated': bool(upload_error is None and 'image_file' in request.files)
                    }
                )
                
                logger.info(f"Обновлен проект: {project.title}")
                return redirect(url_for(f'admin_{jwt_secret}.portfolio'))
                
            except Exception as e:
                logger.error(f"Ошибка обновления проекта: {e}")
                db.session.rollback()
                user = User.get_by_jwt_secret(jwt_secret)
                return render_template('admin/portfolio_form.html', 
                                     user=user,
                                     project=project, 
                                     error="Ошибка обновления проекта",
                                     categories=Portfolio.Category.__dict__,
                                     statuses=Portfolio.Status.__dict__,
                                     jwt_secret=jwt_secret)
        
        user = User.get_by_jwt_secret(jwt_secret)
        return render_template('admin/portfolio_form.html', 
                             user=user,
                             project=project,
                             categories=Portfolio.Category.__dict__,
                             statuses=Portfolio.Status.__dict__,
                             jwt_secret=jwt_secret)
    
    @admin_bp.route('/portfolio/<project_id>/delete', methods=['POST'])
    @admin_required
    def portfolio_delete(project_id):
        """Удаление проекта."""
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            return jsonify({"error": "Неверный ID проекта"}), 400
        
        project = Portfolio.query.get_or_404(project_uuid)
        
        try:
            title = project.title
            
            # Логирование действия админа
            user_id = session.get('admin_user_id')
            log_admin_action(
                action="DELETE",
                resource="portfolio",
                resource_id=str(project.id),
                user_id=user_id,
                details={
                    'title': title,
                    'client': project.client,
                    'category': project.category,
                    'was_featured': project.is_featured,
                    'had_image': bool(project.image_url)
                }
            )
            
            db.session.delete(project)
            db.session.commit()
            
            logger.info(f"Удален проект: {title}")
            return jsonify({"success": True, "message": "Проект удален"})
            
        except Exception as e:
            logger.error(f"Ошибка удаления проекта: {e}")
            db.session.rollback()
            return jsonify({"success": False, "message": "Ошибка удаления проекта"}), 500
    
    # ===== API ROUTES =====
    
    @admin_bp.route('/api/services')
    @admin_required
    def api_services():
        """API для получения услуг."""
        services_list = Service.query.order_by(Service.sort_order).all()
        return jsonify([service.to_dict() for service in services_list])
    
    @admin_bp.route('/api/portfolio')
    @admin_required
    def api_portfolio():
        """API для получения портфолио."""
        portfolio_list = Portfolio.query.order_by(Portfolio.sort_order.desc()).all()
        return jsonify([project.to_dict() for project in portfolio_list])
    
    @admin_bp.route('/logout')
    @admin_required
    def logout():
        """Выход из админки."""
        session.pop('admin_user_id', None)
        return redirect(url_for('main.homepage'))
    
    return admin_bp


def register_admin_routes(app):
    """
    Регистрация всех роутов админки для всех суперпользователей.
    
    Args:
        app: Flask приложение
    """
    with app.app_context():
        try:
            # Получаем всех суперпользователей
            superusers = User.query.filter_by(is_superuser=True, is_active=True).all()
            
            for user in superusers:
                if user.jwt_secret:
                    admin_bp = create_admin_blueprint(user.jwt_secret)
                    app.register_blueprint(admin_bp)
                    logger.info(f"Зарегистрирован админ роут для пользователя {user.email}: /{user.jwt_secret}/admin")
            
            logger.info(f"Зарегистрировано {len(superusers)} админ роутов")
            
        except Exception as e:
            # Если таблица не существует, пропускаем регистрацию роутов
            logger.warning(f"Не удалось зарегистрировать админ роуты: {e}")
            logger.info("База данных еще не инициализирована. Роуты админки будут зарегистрированы после создания суперпользователя.")


def refresh_admin_routes(app):
    """
    Перерегистрация админ роутов после создания новых суперпользователей.
    
    Args:
        app: Flask приложение
    """
    with app.app_context():
        try:
            # Получаем всех суперпользователей
            superusers = User.query.filter_by(is_superuser=True, is_active=True).all()
            
            # Очищаем существующие админ blueprints
            blueprints_to_remove = []
            for bp_name in app.blueprints.keys():
                if bp_name.startswith('admin_'):
                    blueprints_to_remove.append(bp_name)
            
            for bp_name in blueprints_to_remove:
                app.blueprints.pop(bp_name, None)
                logger.info(f"Удален blueprint: {bp_name}")
            
            # Регистрируем новые роуты
            for user in superusers:
                if user.jwt_secret:
                    admin_bp = create_admin_blueprint(user.jwt_secret)
                    app.register_blueprint(admin_bp)
                    logger.info(f"Зарегистрирован админ роут для пользователя {user.email}: /{user.jwt_secret}/admin")
            
            logger.info(f"Перерегистрировано {len(superusers)} админ роутов")
            
        except Exception as e:
            logger.error(f"Ошибка перерегистрации админ роутов: {e}") 