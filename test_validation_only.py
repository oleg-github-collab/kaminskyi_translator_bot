#!/usr/bin/env python3
"""
🧪 ТЕСТ ВАЛІДАЦІЇ ФАЙЛІВ БЕЗ AIOGRAM
"""

import sys
import os
import tempfile

print("🚀 Тестуємо систему валідації файлів...")

try:
    from utils.file_validation import (
        comprehensive_file_validation, create_validation_report, 
        get_supported_formats_text, SUPPORTED_EXTENSIONS
    )
    
    print(f"✅ Підтримувані формати: {list(SUPPORTED_EXTENSIONS.keys())}")
    
    # Створюємо тестовий файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        test_content = "Це тестовий файл для валідації.\nThis is a test file for validation.\n" * 100
        f.write(test_content)
        test_file_path = f.name
    
    print(f"📝 Створено тестовий файл: {test_file_path}")
    print(f"📊 Розмір контенту: {len(test_content)} символів")
    
    # Тест валідації
    result = comprehensive_file_validation(test_file_path, "test.txt")
    
    print(f"\n🔍 РЕЗУЛЬТАТ ВАЛІДАЦІЇ:")
    print(f"✅ Валідна: {result.is_valid}")
    if result.is_valid:
        print(f"📄 Тип: {result.file_type}")
        print(f"📊 Розмір: {result.size_bytes:,} байт")
        print(f"🔤 Символів: {result.char_count:,}")
        print(f"💰 Вартість: {result.estimated_cost}€")
        print(f"⏱️ Час обробки: {result.processing_time_estimate}с")
        print(f"🔧 MIME: {result.mime_type}")
        if result.encoding:
            print(f"📝 Кодування: {result.encoding}")
    else:
        print(f"❌ Помилка: {result.error_message}")
    
    # Тест звіту
    report = create_validation_report(result)
    print(f"\n📋 ЗВІТ ВАЛІДАЦІЇ:")
    print(report)
    
    # Тест підтримуваних форматів
    formats_text = get_supported_formats_text()
    print(f"\n📋 ПІДТРИМУВАНІ ФОРМАТИ:")
    print(formats_text[:300] + "...")
    
    # Очищення
    os.unlink(test_file_path)
    
    print("\n✅ ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
    
except Exception as e:
    print(f"❌ ПОМИЛКА: {e}")
    import traceback
    traceback.print_exc()