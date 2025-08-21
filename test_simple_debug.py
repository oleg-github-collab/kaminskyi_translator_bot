#!/usr/bin/env python3
"""
Тест простої debug системи - перевірка що все працює без aiogram
"""

print("🧪 Тестуємо просту debug систему...")

# Тест 1: Перевірка імпорту simple_debug
try:
    from utils.simple_debug import debug_callback, log_action, log_state_transition, log_user_flow
    print("✅ Тест 1: Імпорт utils.simple_debug - успішно")
except Exception as e:
    print(f"❌ Тест 1: Помилка імпорту utils.simple_debug: {e}")

# Тест 2: Перевірка базового логування
try:
    log_action("test_action", 12345, "testing basic logging")
    print("✅ Тест 2: Базове логування - успішно")
except Exception as e:
    print(f"❌ Тест 2: Помилка базового логування: {e}")

# Тест 3: Перевірка логування переходів
try:
    log_state_transition(12345, "state_old", "state_new", "test_trigger")
    print("✅ Тест 3: Логування переходів - успішно")
except Exception as e:
    print(f"❌ Тест 3: Помилка логування переходів: {e}")

# Тест 4: Перевірка user flow
try:
    log_user_flow(12345, "test_step", {"data": "test"})
    print("✅ Тест 4: User flow логування - успішно")
except Exception as e:
    print(f"❌ Тест 4: Помилка user flow логування: {e}")

# Тест 5: Перевірка декоратора (без виконання)
try:
    @debug_callback
    async def test_func():
        return "test"
    
    print("✅ Тест 5: Декоратор debug_callback - успішно")
except Exception as e:
    print(f"❌ Тест 5: Помилка декоратора: {e}")

# Тест 6: Перевірка створення логів
import os
try:
    if os.path.exists('logs/bot_debug.log'):
        print("✅ Тест 6: Файл логів створено - успішно")
        
        # Читаємо останні рядки
        with open('logs/bot_debug.log', 'r') as f:
            lines = f.readlines()
            if lines:
                print(f"📄 Останній лог: {lines[-1].strip()}")
    else:
        print("⚠️ Тест 6: Файл логів не знайдено")
except Exception as e:
    print(f"❌ Тест 6: Помилка читання логів: {e}")

print("\n🎯 Тестування завершено!")
print("🚀 Просте debug система готова до роботи!")