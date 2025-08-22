#!/usr/bin/env python3
"""
📁 УЛЬТРАПОТУЖНА СИСТЕМА ВАЛІДАЦІЇ ФАЙЛІВ
Виправляє всі помилки валідації даних при завантаженні файлів
"""

import os
import logging
import mimetypes
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
# import magic  # Optional dependency
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class FileValidationResult:
    """Результат валідації файлу"""
    is_valid: bool
    file_type: str
    size_bytes: int
    extension: str
    mime_type: str
    encoding: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    char_count: int = 0
    estimated_cost: float = 0.0
    processing_time_estimate: int = 0  # в секундах

# 📋 КОНФІГУРАЦІЯ ФАЙЛІВ
SUPPORTED_EXTENSIONS = {
    '.txt': {
        'mime_types': ['text/plain', 'text/x-python', 'application/octet-stream'],
        'max_size_mb': 50,
        'description': 'Текстовий файл',
        'icon': '📄'
    },
    '.docx': {
        'mime_types': [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/zip',
            'application/octet-stream'
        ],
        'max_size_mb': 100,
        'description': 'Microsoft Word документ',
        'icon': '📝'
    },
    '.pdf': {
        'mime_types': ['application/pdf', 'application/octet-stream'],
        'max_size_mb': 200,
        'description': 'PDF документ',
        'icon': '📑'
    },
    '.doc': {
        'mime_types': [
            'application/msword', 
            'application/vnd.ms-word',
            'application/octet-stream'
        ],
        'max_size_mb': 100,
        'description': 'Microsoft Word документ (старий формат)',
        'icon': '📝'
    },
    '.rtf': {
        'mime_types': [
            'application/rtf', 
            'text/rtf',
            'application/octet-stream'
        ],
        'max_size_mb': 50,
        'description': 'Rich Text Format',
        'icon': '📄'
    },
    '.odt': {
        'mime_types': [
            'application/vnd.oasis.opendocument.text',
            'application/octet-stream'
        ],
        'max_size_mb': 50,
        'description': 'OpenDocument Text',
        'icon': '📄'
    }
}

# 💰 ЦІНИ ЗА СИМВОЛ
PRICING = {
    'basic': 0.001,  # 0.001€ за символ
    'epic': 0.0015   # 0.0015€ за символ
}

# 🎯 БЕЗПЕЧНІ MIME TYPES
SAFE_MIME_TYPES = set()
for ext_info in SUPPORTED_EXTENSIONS.values():
    SAFE_MIME_TYPES.update(ext_info['mime_types'])

def get_file_hash(file_path: str) -> str:
    """Отримати хеш файлу для унікальної ідентифікації"""
    try:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error computing file hash: {e}")
        return "unknown"

def detect_file_encoding(file_path: str) -> Optional[str]:
    """Визначити кодування текстового файлу"""
    try:
        import chardet
        
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Читаємо перші 10KB
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8') if result else 'utf-8'
    except Exception:
        # Fallback: спробуємо стандартні кодування
        encodings_to_try = ['utf-8', 'windows-1251', 'cp1251', 'latin1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(100)  # Спробуємо прочитати трохи
                return encoding
            except Exception:
                continue
        
        return 'utf-8'  # За замовчуванням

def _simple_file_validation(file_path: str, extension: str) -> Tuple[bool, str, int]:
    """Проста валідація без додаткових залежностей"""
    try:
        if extension == '.txt':
            # Простий підрахунок для txt файлів
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    char_count = len(content)
                    
                    if char_count == 0:
                        return False, "Файл порожній", 0
                    if char_count < 10:
                        return False, f"Файл занадто малий ({char_count} символів)", char_count
                    if char_count > 1_000_000:
                        return False, f"Файл занадто великий ({char_count:,} символів)", char_count
                    
                    return True, "OK", char_count
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='windows-1251') as f:
                        content = f.read()
                        char_count = len(content)
                        if char_count >= 10:
                            return True, "OK", char_count
                        else:
                            return False, f"Файл занадто малий ({char_count} символів)", char_count
                except:
                    return False, "Не вдалося декодувати файл", 0
        else:
            # Для інших форматів без спеціальних бібліотек
            file_size = os.path.getsize(file_path)
            estimated_chars = file_size // 2  # Приблизна оцінка
            return True, "OK", max(100, estimated_chars)  # Мінімум 100 символів
            
    except Exception as e:
        return False, f"Помилка читання: {str(e)}", 0

def get_file_mime_type(file_path: str) -> str:
    """Отримати MIME тип файлу"""
    try:
        # Спочатку пробуємо python-magic якщо доступно
        try:
            import magic
            file_mime = magic.from_file(file_path, mime=True)
            if file_mime:
                logger.debug(f"Magic MIME type for {file_path}: {file_mime}")
                return file_mime
        except (ImportError, Exception) as e:
            logger.debug(f"Magic not available or failed: {e}")
        
        # Fallback: використовуємо mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            logger.debug(f"Mimetypes MIME type for {file_path}: {mime_type}")
            return mime_type
        
        # Додаткова перевірка за розширенням
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.docx':
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif ext == '.pdf':
            return 'application/pdf'
        elif ext == '.txt':
            return 'text/plain'
        elif ext == '.doc':
            return 'application/msword'
        elif ext == '.rtf':
            return 'application/rtf'
        elif ext == '.odt':
            return 'application/vnd.oasis.opendocument.text'
        
        # Якщо нічого не спрацювало
        return 'application/octet-stream'
        
    except Exception as e:
        logger.error(f"Error detecting MIME type for {file_path}: {e}")
        return 'application/octet-stream'

def validate_file_content(file_path: str, extension: str) -> Tuple[bool, str, int]:
    """Валідація вмісту файлу та підрахунок символів"""
    try:
        # Безпечний імпорт
        try:
            from utils.file_utils import count_chars_in_file, read_file_content
        except ImportError:
            # Fallback: простий підрахунок для txt файлів
            return _simple_file_validation(file_path, extension)
        
        # Підрахунок символів
        char_count = count_chars_in_file(file_path)
        
        if char_count == 0:
            return False, "Файл порожній або не вдалося прочитати вміст", 0
        
        # Перевірка на максимальну кількість символів (1M символів)
        MAX_CHARS = 1_000_000
        if char_count > MAX_CHARS:
            return False, f"Файл занадто великий ({char_count:,} символів). Максимум: {MAX_CHARS:,}", char_count
        
        # Перевірка на мінімальну кількість символів
        MIN_CHARS = 10
        if char_count < MIN_CHARS:
            return False, f"Файл занадто малий ({char_count} символів). Мінімум: {MIN_CHARS}", char_count
        
        # Спроба читання змісту для додаткової валідації
        content = read_file_content(file_path)
        if not content or not content.strip():
            return False, "Файл не містить читабельного тексту", char_count
        
        # Перевірка на підозрілий вміст (занадто багато нечитабельних символів)
        if extension in ['.txt', '.rtf']:
            printable_chars = sum(1 for c in content if c.isprintable() or c.isspace())
            if printable_chars < len(content) * 0.8:  # Менше 80% читабельних символів
                return False, "Файл містить занадто багато нечитабельних символів", char_count
        
        logger.info(f"File content validation successful: {char_count:,} chars")
        return True, "OK", char_count
        
    except Exception as e:
        logger.error(f"Error validating file content {file_path}: {e}")
        return False, f"Помилка читання файлу: {str(e)}", 0

def calculate_processing_estimates(char_count: int, model: str = 'basic') -> Tuple[float, int]:
    """Розрахунок вартості та часу обробки"""
    try:
        # Розрахунок вартості
        price_per_char = PRICING.get(model, PRICING['basic'])
        cost = char_count * price_per_char
        
        # Розрахунок часу (приблизно 100 символів в секунду для basic, 80 для epic)
        chars_per_second = 100 if model == 'basic' else 80
        processing_time = max(30, char_count // chars_per_second)  # Мінімум 30 секунд
        
        return round(cost, 2), processing_time
        
    except Exception as e:
        logger.error(f"Error calculating estimates: {e}")
        return 0.0, 60  # Fallback значення

def comprehensive_file_validation(file_path: str, original_filename: str = None) -> FileValidationResult:
    """
    🛡️ УЛЬТРАПОТУЖНА ВАЛІДАЦІЯ ФАЙЛУ
    Перевіряє ВСЕ можливі проблеми
    """
    warnings = []
    
    try:
        logger.info(f"🔍 Starting comprehensive validation for: {file_path}")
        
        # 1. ПЕРЕВІРКА ІСНУВАННЯ ФАЙЛУ
        if not file_path or not os.path.exists(file_path):
            return FileValidationResult(
                is_valid=False,
                file_type="unknown",
                size_bytes=0,
                extension="",
                mime_type="",
                error_message="Файл не існує або шлях некоректний"
            )
        
        # 2. ПЕРЕВІРКА РОЗМІРУ
        try:
            size_bytes = os.path.getsize(file_path)
            logger.info(f"📊 File size: {size_bytes:,} bytes ({size_bytes/1024/1024:.2f} MB)")
        except Exception as e:
            return FileValidationResult(
                is_valid=False,
                file_type="unknown",
                size_bytes=0,
                extension="",
                mime_type="",
                error_message=f"Не вдалося отримати розмір файлу: {e}"
            )
        
        if size_bytes == 0:
            return FileValidationResult(
                is_valid=False,
                file_type="unknown",
                size_bytes=0,
                extension="",
                mime_type="",
                error_message="Файл порожній (0 байт)"
            )
        
        # Максимальний розмір 500MB
        MAX_SIZE_BYTES = 500 * 1024 * 1024
        if size_bytes > MAX_SIZE_BYTES:
            return FileValidationResult(
                is_valid=False,
                file_type="unknown",
                size_bytes=size_bytes,
                extension="",
                mime_type="",
                error_message=f"Файл занадто великий ({size_bytes/1024/1024:.1f} MB). Максимум: {MAX_SIZE_BYTES/1024/1024} MB"
            )
        
        # 3. ВИЗНАЧЕННЯ РОЗШИРЕННЯ
        if original_filename:
            extension = os.path.splitext(original_filename)[1].lower()
        else:
            extension = os.path.splitext(file_path)[1].lower()
        
        logger.info(f"📄 File extension: {extension}")
        
        if not extension:
            return FileValidationResult(
                is_valid=False,
                file_type="unknown",
                size_bytes=size_bytes,
                extension="",
                mime_type="",
                error_message="Файл без розширення"
            )
        
        # 4. ПЕРЕВІРКА ПІДТРИМУВАНОГО ФОРМАТУ
        if extension not in SUPPORTED_EXTENSIONS:
            supported_list = ", ".join(SUPPORTED_EXTENSIONS.keys())
            return FileValidationResult(
                is_valid=False,
                file_type=extension,
                size_bytes=size_bytes,
                extension=extension,
                mime_type="",
                error_message=f"Непідтримуваний формат {extension}. Підтримуються: {supported_list}"
            )
        
        ext_info = SUPPORTED_EXTENSIONS[extension]
        
        # 5. ПЕРЕВІРКА РОЗМІРУ ДЛЯ КОНКРЕТНОГО ТИПУ
        max_size_bytes = ext_info['max_size_mb'] * 1024 * 1024
        if size_bytes > max_size_bytes:
            return FileValidationResult(
                is_valid=False,
                file_type=extension,
                size_bytes=size_bytes,
                extension=extension,
                mime_type="",
                error_message=f"Файл {extension} занадто великий ({size_bytes/1024/1024:.1f} MB). Максимум для {extension}: {ext_info['max_size_mb']} MB"
            )
        
        # 6. ВИЗНАЧЕННЯ MIME TYPE
        mime_type = get_file_mime_type(file_path)
        logger.info(f"🔍 Detected MIME type: {mime_type}")
        
        # 7. ПЕРЕВІРКА MIME TYPE
        if mime_type not in ext_info['mime_types']:
            warning_msg = f"MIME тип {mime_type} не типовий для {extension}"
            warnings.append(warning_msg)
            logger.warning(warning_msg)
            
            # Якщо MIME тип зовсім небезпечний
            if mime_type not in SAFE_MIME_TYPES:
                return FileValidationResult(
                    is_valid=False,
                    file_type=extension,
                    size_bytes=size_bytes,
                    extension=extension,
                    mime_type=mime_type,
                    error_message=f"Небезпечний MIME тип: {mime_type}"
                )
        
        # 8. ВИЗНАЧЕННЯ КОДУВАННЯ ДЛЯ ТЕКСТОВИХ ФАЙЛІВ
        encoding = None
        if extension in ['.txt', '.rtf']:
            encoding = detect_file_encoding(file_path)
            logger.info(f"📝 Detected encoding: {encoding}")
        
        # 9. ВАЛІДАЦІЯ ВМІСТУ ТА ПІДРАХУНОК СИМВОЛІВ
        content_valid, content_error, char_count = validate_file_content(file_path, extension)
        if not content_valid:
            return FileValidationResult(
                is_valid=False,
                file_type=extension,
                size_bytes=size_bytes,
                extension=extension,
                mime_type=mime_type,
                encoding=encoding,
                error_message=content_error,
                char_count=char_count
            )
        
        # 10. РОЗРАХУНОК ВАРТОСТІ ТА ЧАСУ
        estimated_cost, processing_time = calculate_processing_estimates(char_count)
        
        # 11. ДОДАТКОВІ ПОПЕРЕДЖЕННЯ
        if char_count > 500_000:
            warnings.append(f"Великий файл ({char_count:,} символів) - обробка може зайняти {processing_time//60} хв")
        
        if size_bytes > 10 * 1024 * 1024:  # Більше 10MB
            warnings.append(f"Великий розмір файлу ({size_bytes/1024/1024:.1f} MB)")
        
        # 12. УСПІШНИЙ РЕЗУЛЬТАТ
        logger.info(f"✅ File validation successful: {char_count:,} chars, {estimated_cost}€")
        
        return FileValidationResult(
            is_valid=True,
            file_type=ext_info['description'],
            size_bytes=size_bytes,
            extension=extension,
            mime_type=mime_type,
            encoding=encoding,
            warnings=warnings if warnings else None,
            char_count=char_count,
            estimated_cost=estimated_cost,
            processing_time_estimate=processing_time
        )
        
    except Exception as e:
        logger.error(f"❌ Critical error in file validation: {e}", exc_info=True)
        return FileValidationResult(
            is_valid=False,
            file_type="unknown",
            size_bytes=0,
            extension="",
            mime_type="",
            error_message=f"Критична помилка валідації: {str(e)}"
        )

def get_supported_formats_text() -> str:
    """Отримати текст з підтримуваними форматами"""
    formats = []
    for ext, info in SUPPORTED_EXTENSIONS.items():
        formats.append(f"{info['icon']} {ext.upper()} - {info['description']} (до {info['max_size_mb']} MB)")
    
    return "📋 **Підтримувані формати:**\n\n" + "\n".join(formats)

def create_validation_report(result: FileValidationResult) -> str:
    """Створити детальний звіт про валідацію"""
    if not result.is_valid:
        return f"❌ **Помилка валідації:**\n{result.error_message}"
    
    report = [
        f"✅ **Файл пройшов валідацію**",
        f"📄 **Тип:** {result.file_type}",
        f"📊 **Розмір:** {result.size_bytes:,} байт ({result.size_bytes/1024/1024:.2f} MB)",
        f"🔤 **Символів:** {result.char_count:,}",
        f"💰 **Орієнтовна вартість:** {result.estimated_cost}€",
        f"⏱️ **Час обробки:** ~{result.processing_time_estimate//60} хв {result.processing_time_estimate%60} сек"
    ]
    
    if result.encoding:
        report.append(f"📝 **Кодування:** {result.encoding}")
    
    if result.warnings:
        report.append(f"\n⚠️ **Попередження:**")
        for warning in result.warnings:
            report.append(f"• {warning}")
    
    return "\n".join(report)

# Експорт
__all__ = [
    'FileValidationResult', 'comprehensive_file_validation', 
    'get_supported_formats_text', 'create_validation_report',
    'SUPPORTED_EXTENSIONS', 'PRICING'
]

if __name__ == "__main__":
    # Тест системи валідації
    print("🧪 Тестуємо систему валідації файлів...")
    
    print(f"📋 Підтримувані формати: {list(SUPPORTED_EXTENSIONS.keys())}")
    print(f"🔒 Безпечні MIME types: {len(SAFE_MIME_TYPES)}")
    print(f"💰 Ціни: {PRICING}")
    
    print("\n" + get_supported_formats_text())
    
    print("\n🚀 Система валідації готова!")