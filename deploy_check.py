#!/usr/bin/env python3
"""
Скрипт для проверки состояния развертывания приложения.
Диагностика и проверка всех компонентов.
"""

import os
import sys
import subprocess
import psutil
from datetime import datetime

# Добавляем корневую директорию в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_git_status():
    """Проверка статуса Git репозитория."""
    print("🔍 Проверка Git статуса...")
    
    try:
        # Проверяем есть ли uncommitted изменения
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  Есть неcommitted изменения:")
            print(result.stdout)
        else:
            print("✅ Рабочая директория чистая")
        
        # Проверяем последний коммит
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True)
        print(f"📝 Последний коммит: {result.stdout.strip()}")
        
        # Проверяем ветку
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True)
        print(f"🌿 Текущая ветка: {result.stdout.strip()}")
        
    except Exception as e:
        print(f"❌ Ошибка проверки Git: {e}")


def check_gunicorn_processes():
    """Проверка процессов Gunicorn."""
    print("\n🔍 Проверка процессов Gunicorn...")
    
    gunicorn_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if 'gunicorn' in proc.info['name'] or \
               any('gunicorn' in cmd for cmd in proc.info['cmdline']):
                gunicorn_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if gunicorn_processes:
        print(f"✅ Найдено {len(gunicorn_processes)} Gunicorn процессов:")
        for proc in gunicorn_processes:
            start_time = datetime.fromtimestamp(proc['create_time'])
            print(f"  📍 PID: {proc['pid']}, запущен: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ Процессы Gunicorn не найдены!")


def check_port_listening():
    """Проверка что порт 8000 прослушивается."""
    print("\n🔍 Проверка порта 8000...")
    
    try:
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        if ':8000' in result.stdout:
            lines = [line for line in result.stdout.split('\n') if ':8000' in line]
            for line in lines:
                print(f"✅ Порт прослушивается: {line.strip()}")
        else:
            print("❌ Порт 8000 не прослушивается!")
    except Exception as e:
        print(f"❌ Ошибка проверки порта: {e}")


def check_app_response():
    """Проверка ответа приложения."""
    print("\n🔍 Проверка ответа приложения...")
    
    try:
        result = subprocess.run(['curl', '-I', 'http://127.0.0.1:8000/'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if '200 OK' in result.stdout:
                print("✅ Приложение отвечает корректно")
            else:
                print(f"⚠️  Приложение отвечает с ошибкой:\n{result.stdout}")
        else:
            print(f"❌ Ошибка запроса: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Timeout при запросе к приложению")
    except Exception as e:
        print(f"❌ Ошибка проверки приложения: {e}")


def check_database():
    """Проверка базы данных."""
    print("\n🔍 Проверка базы данных...")
    
    try:
        from app import create_app, db
        from app.models import User, Service, Portfolio
        
        app = create_app('production')
        with app.app_context():
            # Проверяем подключение к БД
            result = db.session.execute('SELECT 1')
            print("✅ Подключение к БД работает")
            
            # Считаем записи в основных таблицах
            users_count = User.query.count()
            services_count = Service.query.count()
            portfolio_count = Portfolio.query.count()
            
            print(f"📊 Статистика БД:")
            print(f"  👥 Пользователей: {users_count}")
            print(f"  🛠  Услуг: {services_count}")
            print(f"  📁 Проектов в портфолио: {portfolio_count}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")


def check_logs():
    """Проверка логов."""
    print("\n🔍 Проверка логов...")
    
    log_files = [
        'logs/error.log',
        'logs/access.log',
        'logs/errors.log',
        'logs/app.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            print(f"📄 {log_file}: {size} байт, изменён: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Показываем последние ошибки
            if 'error' in log_file:
                try:
                    result = subprocess.run(['tail', '-5', log_file], 
                                          capture_output=True, text=True)
                    if result.stdout.strip():
                        print(f"  📋 Последние записи:")
                        for line in result.stdout.strip().split('\n'):
                            print(f"    {line}")
                except Exception:
                    pass
        else:
            print(f"❌ {log_file} не найден")


def main():
    """Основная функция проверки."""
    print("🚀 Диагностика состояния развертывания")
    print("=" * 50)
    
    check_git_status()
    check_gunicorn_processes()
    check_port_listening()
    check_app_response()
    check_database()
    check_logs()
    
    print("\n" + "=" * 50)
    print("✅ Диагностика завершена")


if __name__ == '__main__':
    main() 