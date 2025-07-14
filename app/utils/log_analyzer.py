"""
Анализатор логов.
Утилиты для анализа, мониторинга и агрегации логов.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LogEntry:
    """Структура записи лога."""
    timestamp: datetime
    level: str
    source: str
    message: str
    extra_data: Dict[str, Any] = None


@dataclass
class LogStats:
    """Статистика логов."""
    total_entries: int
    by_level: Dict[str, int]
    by_source: Dict[str, int]
    by_hour: Dict[str, int]
    errors_count: int
    warnings_count: int
    requests_count: int
    admin_actions: int
    file_operations: int
    security_events: int


class LogAnalyzer:
    """Анализатор логов приложения."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Инициализация анализатора.
        
        Args:
            log_dir: Директория с логами
        """
        self.log_dir = Path(log_dir)
        self.log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \| (\w+)\s*\| ([^|]+) \| (.+)'
        )
    
    def parse_log_line(self, line: str) -> Optional[LogEntry]:
        """
        Парсинг строки лога.
        
        Args:
            line: Строка лога
            
        Returns:
            LogEntry или None если не удалось распарсить
        """
        match = self.log_pattern.match(line.strip())
        if not match:
            return None
        
        timestamp_str, level, source, message = match.groups()
        
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return None
        
        return LogEntry(
            timestamp=timestamp,
            level=level.strip(),
            source=source.strip(),
            message=message.strip()
        )
    
    def read_log_file(self, file_path: Path, since: datetime = None) -> List[LogEntry]:
        """
        Чтение файла логов.
        
        Args:
            file_path: Путь к файлу
            since: Читать логи с определенного времени
            
        Returns:
            Список записей логов
        """
        entries = []
        
        if not file_path.exists():
            return entries
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = self.parse_log_line(line)
                    if entry and (since is None or entry.timestamp >= since):
                        entries.append(entry)
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
        
        return entries
    
    def get_log_files(self) -> List[Path]:
        """
        Получение списка файлов логов.
        
        Returns:
            Список путей к файлам логов
        """
        if not self.log_dir.exists():
            return []
        
        return [f for f in self.log_dir.glob("*.log") if f.is_file()]
    
    def analyze_logs(self, since: datetime = None, log_types: List[str] = None) -> LogStats:
        """
        Анализ логов.
        
        Args:
            since: Анализировать логи с определенного времени
            log_types: Типы логов для анализа
            
        Returns:
            Статистика логов
        """
        all_entries = []
        
        # Получаем все файлы логов
        log_files = self.get_log_files()
        
        # Фильтруем по типам если указано
        if log_types:
            log_files = [f for f in log_files 
                        if any(log_type in f.name for log_type in log_types)]
        
        # Читаем все файлы
        for file_path in log_files:
            entries = self.read_log_file(file_path, since)
            all_entries.extend(entries)
        
        # Анализируем записи
        return self._calculate_stats(all_entries)
    
    def _calculate_stats(self, entries: List[LogEntry]) -> LogStats:
        """
        Вычисление статистики по записям.
        
        Args:
            entries: Список записей логов
            
        Returns:
            Статистика
        """
        by_level = Counter()
        by_source = Counter()
        by_hour = Counter()
        
        errors_count = 0
        warnings_count = 0
        requests_count = 0
        admin_actions = 0
        file_operations = 0
        security_events = 0
        
        for entry in entries:
            # Статистика по уровням
            by_level[entry.level] += 1
            
            # Статистика по источникам
            by_source[entry.source] += 1
            
            # Статистика по часам
            hour_key = entry.timestamp.strftime('%H:00')
            by_hour[hour_key] += 1
            
            # Подсчет специальных типов
            message = entry.message.upper()
            
            if entry.level in ['ERROR', 'CRITICAL']:
                errors_count += 1
            elif entry.level == 'WARNING':
                warnings_count += 1
            
            if 'REQUEST' in message or 'RESPONSE' in message:
                requests_count += 1
            
            if 'ADMIN' in message:
                admin_actions += 1
            
            if any(keyword in message for keyword in ['UPLOAD', 'FILE', 'IMAGE', 'DELETE']):
                file_operations += 1
            
            if any(keyword in message for keyword in ['AUTH', 'LOGIN', 'SECURITY', 'JWT']):
                security_events += 1
        
        return LogStats(
            total_entries=len(entries),
            by_level=dict(by_level),
            by_source=dict(by_source),
            by_hour=dict(by_hour),
            errors_count=errors_count,
            warnings_count=warnings_count,
            requests_count=requests_count,
            admin_actions=admin_actions,
            file_operations=file_operations,
            security_events=security_events
        )
    
    def find_errors(self, since: datetime = None, limit: int = 50) -> List[LogEntry]:
        """
        Поиск ошибок в логах.
        
        Args:
            since: Искать ошибки с определенного времени
            limit: Максимальное количество ошибок
            
        Returns:
            Список ошибок
        """
        errors = []
        
        # Читаем файл ошибок
        error_file = self.log_dir / "errors.log"
        if error_file.exists():
            entries = self.read_log_file(error_file, since)
            errors.extend([e for e in entries if e.level in ['ERROR', 'CRITICAL']])
        
        # Читаем основной файл для дополнительных ошибок
        app_file = self.log_dir / "app.log"
        if app_file.exists():
            entries = self.read_log_file(app_file, since)
            errors.extend([e for e in entries if e.level in ['ERROR', 'CRITICAL']])
        
        # Сортируем по времени (новые сначала)
        errors.sort(key=lambda x: x.timestamp, reverse=True)
        
        return errors[:limit]
    
    def find_slow_requests(self, threshold: float = 1.0, since: datetime = None) -> List[LogEntry]:
        """
        Поиск медленных запросов.
        
        Args:
            threshold: Порог времени в секундах
            since: Искать с определенного времени
            
        Returns:
            Список медленных запросов
        """
        slow_requests = []
        
        # Читаем файл производительности
        perf_file = self.log_dir / "performance.log"
        if perf_file.exists():
            entries = self.read_log_file(perf_file, since)
            for entry in entries:
                # Ищем время выполнения в сообщении
                time_match = re.search(r'(\d+\.\d+)s', entry.message)
                if time_match:
                    duration = float(time_match.group(1))
                    if duration >= threshold:
                        slow_requests.append(entry)
        
        # Читаем файл запросов
        requests_file = self.log_dir / "requests.log"
        if requests_file.exists():
            entries = self.read_log_file(requests_file, since)
            for entry in entries:
                if 'RESPONSE' in entry.message:
                    time_match = re.search(r'\((\d+\.\d+)s\)', entry.message)
                    if time_match:
                        duration = float(time_match.group(1))
                        if duration >= threshold:
                            slow_requests.append(entry)
        
        # Сортируем по времени
        slow_requests.sort(key=lambda x: x.timestamp, reverse=True)
        
        return slow_requests
    
    def get_security_events(self, since: datetime = None) -> List[LogEntry]:
        """
        Получение событий безопасности.
        
        Args:
            since: Получить события с определенного времени
            
        Returns:
            Список событий безопасности
        """
        events = []
        
        security_file = self.log_dir / "security.log"
        if security_file.exists():
            entries = self.read_log_file(security_file, since)
            events.extend(entries)
        
        # Сортируем по времени (новые сначала)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events
    
    def generate_report(self, since: datetime = None) -> Dict[str, Any]:
        """
        Генерация отчета по логам.
        
        Args:
            since: Генерировать отчет с определенного времени
            
        Returns:
            Словарь с отчетом
        """
        if since is None:
            since = datetime.now() - timedelta(hours=24)
        
        stats = self.analyze_logs(since)
        errors = self.find_errors(since, limit=10)
        slow_requests = self.find_slow_requests(threshold=1.0, since=since)
        security_events = self.get_security_events(since)
        
        return {
            'period': {
                'from': since.isoformat(),
                'to': datetime.now().isoformat()
            },
            'summary': {
                'total_entries': stats.total_entries,
                'errors': stats.errors_count,
                'warnings': stats.warnings_count,
                'requests': stats.requests_count,
                'admin_actions': stats.admin_actions,
                'file_operations': stats.file_operations,
                'security_events': stats.security_events
            },
            'breakdown': {
                'by_level': stats.by_level,
                'by_source': stats.by_source,
                'by_hour': stats.by_hour
            },
            'issues': {
                'recent_errors': [
                    {
                        'timestamp': error.timestamp.isoformat(),
                        'level': error.level,
                        'source': error.source,
                        'message': error.message
                    }
                    for error in errors
                ],
                'slow_requests': [
                    {
                        'timestamp': req.timestamp.isoformat(),
                        'message': req.message
                    }
                    for req in slow_requests[:5]
                ],
                'security_events': [
                    {
                        'timestamp': event.timestamp.isoformat(),
                        'level': event.level,
                        'message': event.message
                    }
                    for event in security_events[:10]
                ]
            }
        }
    
    def clean_old_logs(self, days: int = 30) -> int:
        """
        Очистка старых логов.
        
        Args:
            days: Количество дней для хранения
            
        Returns:
            Количество удаленных файлов
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for file_path in self.get_log_files():
            try:
                # Проверяем дату модификации файла
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"Удален старый лог файл: {file_path.name}")
            except Exception as e:
                print(f"Ошибка удаления файла {file_path}: {e}")
        
        return deleted_count


def create_log_analyzer() -> LogAnalyzer:
    """
    Создание анализатора логов.
    
    Returns:
        Настроенный анализатор логов
    """
    return LogAnalyzer()


# CLI функции для работы с логами
def print_log_stats(days: int = 1):
    """Вывод статистики логов за последние дни."""
    analyzer = create_log_analyzer()
    since = datetime.now() - timedelta(days=days)
    
    stats = analyzer.analyze_logs(since)
    
    print(f"\n=== Статистика логов за последние {days} дн. ===")
    print(f"Всего записей: {stats.total_entries}")
    print(f"Ошибки: {stats.errors_count}")
    print(f"Предупреждения: {stats.warnings_count}")
    print(f"HTTP запросы: {stats.requests_count}")
    print(f"Действия админа: {stats.admin_actions}")
    print(f"Файловые операции: {stats.file_operations}")
    print(f"События безопасности: {stats.security_events}")
    
    if stats.by_level:
        print("\nПо уровням:")
        for level, count in sorted(stats.by_level.items()):
            print(f"  {level}: {count}")


def print_recent_errors(limit: int = 10):
    """Вывод последних ошибок."""
    analyzer = create_log_analyzer()
    errors = analyzer.find_errors(limit=limit)
    
    print(f"\n=== Последние {len(errors)} ошибок ===")
    for error in errors:
        print(f"{error.timestamp.strftime('%Y-%m-%d %H:%M:%S')} [{error.level}] {error.source}")
        print(f"  {error.message}")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            print_log_stats(days)
        
        elif command == "errors":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            print_recent_errors(limit)
        
        elif command == "report":
            analyzer = create_log_analyzer()
            since = datetime.now() - timedelta(hours=24)
            report = analyzer.generate_report(since)
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        elif command == "clean":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            analyzer = create_log_analyzer()
            deleted = analyzer.clean_old_logs(days)
            print(f"Удалено {deleted} старых файлов логов")
    
    else:
        print("Использование:")
        print("  python log_analyzer.py stats [days]     - статистика за дни")
        print("  python log_analyzer.py errors [limit]   - последние ошибки")
        print("  python log_analyzer.py report           - полный отчет")
        print("  python log_analyzer.py clean [days]     - очистка старых логов") 