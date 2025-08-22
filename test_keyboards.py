#!/usr/bin/env python3
"""
Тест клавіатур мов
"""

import sys
import os

# Додаємо поточну директорію до шляху
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_language_keyboards():
    """Тестуємо клавіатури мов"""
    print("🧪 === ТЕСТ КЛАВІАТУР МОВ ===")
    
    try:
        # Імпортуємо необхідні модулі
        from keyboards.inline import get_language_keyboard
        from config import DEEPL_LANGUAGES, OTRANSLATOR_LANGUAGES, COMMON_LANGUAGES
        
        print(f"✅ Модулі імпортовано успішно")
        
        # Тестуємо кількість мов
        print(f"\n📊 Кількість мов:")
        print(f"   DeepL: {len(DEEPL_LANGUAGES)} мов")
        print(f"   O*Translator: {len(OTRANSLATOR_LANGUAGES)} мов")  
        print(f"   Популярні: {len(COMMON_LANGUAGES)} мов")
        
        # Тестуємо створення клавіатур
        print(f"\n🔘 Створюємо клавіатури:")
        
        # Basic модель (DeepL)
        basic_kb = get_language_keyboard("basic", page=0)
        print(f"   Basic (DeepL): {len(basic_kb.inline_keyboard)} рядків")
        
        # Epic модель (O*Translator)  
        epic_kb = get_language_keyboard("epic", page=0)
        print(f"   Epic (O*Translator): {len(epic_kb.inline_keyboard)} рядків")
        
        # Тестуємо пагінацію
        print(f"\n📄 Тестуємо пагінацію:")
        page_2 = get_language_keyboard("epic", page=1)
        print(f"   Сторінка 2 (Epic): {len(page_2.inline_keyboard)} рядків")
        
        # Показуємо перші кілька мов для DeepL
        print(f"\n🌍 Перші мови DeepL:")
        deepl_list = list(DEEPL_LANGUAGES.items())[:5]
        for code, name in deepl_list:
            display = COMMON_LANGUAGES.get(code, name)
            print(f"   {code}: {display}")
        
        # Показуємо перші кілька мов для O*Translator
        print(f"\n🌐 Перші мови O*Translator:")
        otrans_list = list(OTRANSLATOR_LANGUAGES.items())[:5]
        for code, name in otrans_list:
            display = COMMON_LANGUAGES.get(code, name)
            print(f"   {code}: {display}")
        
        print(f"\n✅ Всі тести пройдено успішно!")
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_language_keyboards()
    sys.exit(0 if success else 1)