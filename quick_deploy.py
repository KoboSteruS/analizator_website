#!/usr/bin/env python3
"""
Скрипт для быстрого развертывания приложения на сервере.
Автоматизирует процесс обновления и перезапуска.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def run_command(cmd, description="", check=True):
    """Выполнение команды с логированием."""
    print(f"🔄 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                               capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды: {e}")
        if e.stderr:
            print(f"   Stderr: {e.stderr.strip()}")
        return False

def kill_gunicorn():
    """Остановка всех процессов gunicorn."""
    print("🛑 Остановка gunicorn...")
    
    # Мягкая остановка
    run_command("pkill -TERM -f 'gunicorn.*run:app'", 
                "Отправка SIGTERM gunicorn процессам", check=False)
    
    time.sleep(3)
    
    # Принудительная остановка если нужно
    run_command("pkill -KILL -f 'gunicorn.*run:app'", 
                "Принудительная остановка gunicorn", check=False)
    
    time.sleep(1)
    
    # Проверяем что процессы остановлены
    result = subprocess.run("pgrep -f 'gunicorn.*run:app'", 
                           shell=True, capture_output=True)
    if result.returncode == 0:
        print("⚠️ Некоторые процессы gunicorn все еще запущены")
        return False
    else:
        print("✅ Все процессы gunicorn остановлены")
        return True

def update_code():
    """Обновление кода из git."""
    print("📥 Обновление кода...")
    
    # Проверяем git статус
    result = subprocess.run("git status --porcelain", 
                           shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️ Есть незакоммиченные изменения:")
        print(result.stdout)
        
        response = input("Продолжить? (y/N): ").lower()
        if response != 'y':
            print("❌ Развертывание отменено")
            return False
    
    # Получаем изменения
    if not run_command("git pull origin main", "Получение изменений из git"):
        return False
    
    return True

def clear_cache():
    """Очистка Python кэша."""
    print("🧹 Очистка кэша...")
    
    run_command("find . -name '*.pyc' -delete", 
                "Удаление .pyc файлов", check=False)
    run_command("find . -name '__pycache__' -type d -exec rm -rf {} +", 
                "Удаление __pycache__ директорий", check=False)
    
    print("✅ Кэш очищен")
    return True

def run_diagnostics():
    """Запуск диагностики."""
    print("🩺 Запуск диагностики...")
    
    if not Path("diagnose_gunicorn.py").exists():
        print("⚠️ Файл diagnose_gunicorn.py не найден, пропускаем диагностику")
        return True
    
    result = subprocess.run("python3 diagnose_gunicorn.py", 
                           shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Ошибки: {result.stderr}")
    
    if result.returncode != 0:
        print("❌ Диагностика показала проблемы")
        response = input("Продолжить развертывание? (y/N): ").lower()
        return response == 'y'
    
    print("✅ Диагностика прошла успешно")
    return True

def start_gunicorn():
    """Запуск gunicorn."""
    print("🚀 Запуск gunicorn...")
    
    # Устанавливаем переменные окружения
    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'
    
    # Команда запуска
    cmd = [
        "gunicorn",
        "--bind", "127.0.0.1:8000",
        "--workers", "2",
        "--timeout", "30",
        "--preload",
        "--daemon",
        "--access-logfile", "logs/access.log",
        "--error-logfile", "logs/error.log",
        "--log-level", "info",
        "run_safe:app"  # Используем безопасную версию
    ]
    
    try:
        subprocess.run(cmd, check=True, env=env)
        print("✅ Gunicorn запущен")
        
        # Ждем немного и проверяем что процесс запущен
        time.sleep(2)
        result = subprocess.run("pgrep -f 'gunicorn.*run_safe:app'", 
                               shell=True, capture_output=True)
        if result.returncode == 0:
            print("✅ Gunicorn процесс работает")
            return True
        else:
            print("❌ Gunicorn процесс не найден")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска gunicorn: {e}")
        return False

def check_health():
    """Проверка работоспособности приложения."""
    print("🔍 Проверка работоспособности...")
    
    time.sleep(3)  # Даем время приложению запуститься
    
    try:
        result = subprocess.run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/", 
                               shell=True, capture_output=True, text=True, timeout=10)
        
        status_code = result.stdout.strip()
        if status_code == "200":
            print("✅ Приложение отвечает корректно")
            return True
        else:
            print(f"⚠️ Приложение вернуло код: {status_code}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при проверке приложения")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки приложения: {e}")
        return False

def show_status():
    """Показ статуса приложения."""
    print("\n" + "="*50)
    print("📊 СТАТУС РАЗВЕРТЫВАНИЯ")
    print("="*50)
    
    # Проверяем процессы
    result = subprocess.run("ps aux | grep -E 'gunicorn.*run_safe:app' | grep -v grep", 
                           shell=True, capture_output=True, text=True)
    if result.stdout:
        print("🟢 Gunicorn процессы:")
        print(result.stdout)
    else:
        print("🔴 Gunicorn процессы не найдены")
    
    # Проверяем порт
    result = subprocess.run("netstat -tlnp 2>/dev/null | grep :8000 || ss -tlnp | grep :8000", 
                           shell=True, capture_output=True, text=True)
    if result.stdout:
        print("🟢 Порт 8000 слушается:")
        print(result.stdout.strip())
    else:
        print("🔴 Порт 8000 не слушается")
    
    # Проверяем логи
    if Path("logs/error.log").exists():
        print("\n📄 Последние записи в error.log:")
        run_command("tail -5 logs/error.log", check=False)
    
    print("="*50)

def main():
    """Основная функция развертывания."""
    print("🚀 БЫСТРОЕ РАЗВЕРТЫВАНИЕ ПРИЛОЖЕНИЯ")
    print("="*50)
    
    steps = [
        ("Остановка gunicorn", kill_gunicorn),
        ("Обновление кода", update_code),
        ("Очистка кэша", clear_cache),
        ("Диагностика", run_diagnostics),
        ("Запуск gunicorn", start_gunicorn),
        ("Проверка работоспособности", check_health)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Ошибка на этапе: {step_name}")
            show_status()
            return False
    
    print("\n✅ Развертывание завершено успешно!")
    show_status()
    
    print("\n🎯 Полезные команды:")
    print("  Мониторинг логов: tail -f logs/error.log")
    print("  Проверка процессов: ps aux | grep gunicorn")
    print("  Тест сайта: curl -I http://127.0.0.1:8000/")
    
    return True

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--kill-only':
            kill_gunicorn()
        else:
            main()
    except KeyboardInterrupt:
        print("\n🛑 Развертывание прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 