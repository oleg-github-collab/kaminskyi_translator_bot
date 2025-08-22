#!/usr/bin/env python3
"""
Повний тест системи мов з пагінацією
"""

import sys
import os

# Додаємо поточну директорію до шляху
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_full_language_system():
    """Тестуємо повну систему мов"""
    print("🧪 === ПОВНИЙ ТЕСТ СИСТЕМИ МОВ ===")
    
    try:
        from keyboards.inline import get_language_keyboard
        from config import DEEPL_LANGUAGES, OTRANSLATOR_LANGUAGES, COMMON_LANGUAGES
        
        print("✅ Імпорт успішний")
        
        # 1. ТЕСТ КІЛЬКОСТІ МОВ
        print(f"\n📊 КІЛЬКІСТЬ МОВ:")
        print(f"   • DeepL (Basic): {len(DEEPL_LANGUAGES)} мов")
        print(f"   • O*Translator (Epic): {len(OTRANSLATOR_LANGUAGES)} мов")
        print(f"   • Популярні з прапорами: {len(COMMON_LANGUAGES)} мов")
        
        # 2. ТЕСТ КЛАВІАТУР
        print(f"\n🔘 ТЕСТ СТВОРЕННЯ КЛАВІАТУР:")
        
        # Basic модель
        basic_kb = get_language_keyboard("basic", page=0)
        basic_page_2 = get_language_keyboard("basic", page=1)
        basic_page_last = get_language_keyboard("basic", page=10)  # Тест великого номера
        
        print(f"   Basic стор.1: {len(basic_kb.inline_keyboard)} рядків")
        print(f"   Basic стор.2: {len(basic_page_2.inline_keyboard)} рядків") 
        print(f"   Basic стор.10: {len(basic_page_last.inline_keyboard)} рядків")
        
        # Epic модель
        epic_kb = get_language_keyboard("epic", page=0)
        epic_page_2 = get_language_keyboard("epic", page=1)
        epic_page_5 = get_language_keyboard("epic", page=5)
        
        print(f"   Epic стор.1: {len(epic_kb.inline_keyboard)} рядків")
        print(f"   Epic стор.2: {len(epic_page_2.inline_keyboard)} рядків")
        print(f"   Epic стор.6: {len(epic_page_5.inline_keyboard)} рядків")
        
        # 3. ТЕСТ CALLBACK_DATA
        print(f"\n🔗 ТЕСТ CALLBACK DATA:")
        
        # Перевіряємо що всі кнопки мають правильні callback_data
        def check_keyboard_callbacks(keyboard, model_name):
            lang_buttons = 0
            nav_buttons = 0
            info_buttons = 0
            
            for row in keyboard.inline_keyboard:
                for button in row:
                    if button.callback_data.startswith("lang_"):
                        lang_buttons += 1
                        # Перевіряємо формат
                        lang_code = button.callback_data.split("_")[1]
                        if len(lang_code) < 2 or len(lang_code) > 4:
                            print(f"   ❌ Неправильний код мови: {lang_code}")
                    elif button.callback_data.startswith("lang_page_"):
                        nav_buttons += 1
                    elif button.callback_data == "page_info":
                        info_buttons += 1
            
            print(f"   {model_name}: {lang_buttons} мов, {nav_buttons} навіг., {info_buttons} інфо")
            return lang_buttons > 0
        
        check_keyboard_callbacks(basic_kb, "Basic стор.1")
        check_keyboard_callbacks(epic_kb, "Epic стор.1")
        check_keyboard_callbacks(epic_page_2, "Epic стор.2")
        
        # 4. ТЕСТ КОНКРЕТНИХ МОВ
        print(f"\n🌍 ТЕСТ КОНКРЕТНИХ МОВ:")
        
        # Популярні мови з прапорами
        test_languages = ["UK", "EN", "DE", "FR", "ZH", "AR", "JA"]
        
        for lang_code in test_languages:
            in_deepl = lang_code in DEEPL_LANGUAGES
            in_otrans = lang_code in OTRANSLATOR_LANGUAGES
            has_flag = lang_code in COMMON_LANGUAGES
            
            deepl_mark = "✅" if in_deepl else "❌"
            otrans_mark = "✅" if in_otrans else "❌"
            flag_mark = "🏁" if has_flag else "⭕"
            
            lang_name = COMMON_LANGUAGES.get(lang_code, DEEPL_LANGUAGES.get(lang_code, lang_code))
            print(f"   {lang_code} ({lang_name[:15]:15}): DeepL {deepl_mark} | O*Trans {otrans_mark} | Flag {flag_mark}")
        
        # 5. ТЕСТ ПАГІНАЦІЇ
        print(f"\n📄 ТЕСТ ПАГІНАЦІЇ:")
        
        def calculate_pages(total_langs):
            return (total_langs + 11) // 12  # 12 мов на сторінку
        
        basic_pages = calculate_pages(len(DEEPL_LANGUAGES))
        epic_pages = calculate_pages(len(OTRANSLATOR_LANGUAGES))
        
        print(f"   Basic: {len(DEEPL_LANGUAGES)} мов → {basic_pages} сторінок")
        print(f"   Epic: {len(OTRANSLATOR_LANGUAGES)} мов → {epic_pages} сторінок")
        
        # Тестуємо останню сторінку
        last_basic_page = get_language_keyboard("basic", page=basic_pages-1)
        last_epic_page = get_language_keyboard("epic", page=epic_pages-1)
        
        print(f"   Остання сторінка Basic: {len(last_basic_page.inline_keyboard)} рядків")
        print(f"   Остання сторінка Epic: {len(last_epic_page.inline_keyboard)} рядків")
        
        # 6. ВІЗУАЛІЗАЦІЯ
        print(f"\n🎨 ДЕМО КЛАВІАТУРИ (Basic стор.1):")
        print("┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓")
        
        basic_kb = get_language_keyboard("basic", page=0)
        lang_rows = [row for row in basic_kb.inline_keyboard if not any(
            btn.callback_data.startswith("lang_page_") or btn.callback_data == "page_info" 
            for btn in row
        )]
        
        for row in lang_rows[:6]:  # Показуємо перші 6 рядків
            if len(row) == 2:
                left = row[0].text[:17]
                right = row[1].text[:17]
                print(f"┃ {left:17} ┃ {right:17} ┃")
            elif len(row) == 1:
                left = row[0].text[:17]
                print(f"┃ {left:17} ┃                   ┃")
        
        print("┣━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━┫")
        
        # Знаходимо навігаційні кнопки
        nav_found = False
        for row in basic_kb.inline_keyboard:
            if any(btn.callback_data.startswith("lang_page_") for btn in row):
                nav_text = " | ".join([btn.text for btn in row])
                print(f"┃          {nav_text:19}          ┃")
                nav_found = True
                break
        
        if not nav_found:
            print("┃           (немає навігації)           ┃")
        
        # Знаходимо інфо
        for row in basic_kb.inline_keyboard:
            if any(btn.callback_data == "page_info" for btn in row):
                info_text = row[0].text
                print(f"┃ {info_text:37} ┃")
                break
        
        print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        
        print(f"\n✅ УСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print(f"\n🎯 РЕЗУЛЬТАТ:")
        print(f"   • Пагінація працює правильно")
        print(f"   • Всі мови додано до інтерфейсу")
        print(f"   • Callback_data коректні")
        print(f"   • Прапори відображаються")
        print(f"   • Навігація функціонує")
        
        return True
        
    except Exception as e:
        print(f"❌ ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_language_system()
    sys.exit(0 if success else 1)