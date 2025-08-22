#!/usr/bin/env python3
"""
Демонстрація того, як виглядатиме клавіатура в Telegram
"""

def simulate_keyboard_layout():
    """Симулює як буде виглядати клавіатура в Telegram"""
    
    # DeepL Languages з прапорами
    deepl_with_flags = [
        ("AR", "🇸🇦 العربية"), ("BG", "🇧🇬 Български"), 
        ("ZH", "🇨🇳 中文"), ("CS", "🇨🇿 Čeština"),
        ("DA", "🇩🇰 Dansk"), ("NL", "🇳🇱 Nederlands"),
        ("EN", "🇬🇧 English"), ("ET", "Estonian"),
        ("FI", "🇫🇮 Suomi"), ("FR", "🇫🇷 Français"),
        ("DE", "🇩🇪 Deutsch"), ("EL", "🇬🇷 Ελληνικά"),
        ("HE", "🇮🇱 עברית"), ("HU", "🇭🇺 Magyar")
    ]
    
    print("📱 === ЯК ВИГЛЯДАЄ КЛАВІАТУРА В TELEGRAM ===")
    print("\n⚡ KAMINSKYI BASIC - Сторінка 1/3:")
    print("┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓")
    
    # Показуємо перші 14 мов (7 рядків по 2)
    for i in range(0, min(14, len(deepl_with_flags)), 2):
        left = deepl_with_flags[i][1][:17] if len(deepl_with_flags[i][1]) <= 17 else deepl_with_flags[i][1][:14] + "..."
        
        if i + 1 < len(deepl_with_flags):
            right = deepl_with_flags[i+1][1][:17] if len(deepl_with_flags[i+1][1]) <= 17 else deepl_with_flags[i+1][1][:14] + "..."
        else:
            right = ""
            
        print(f"┃ {left:17} ┃ {right:17} ┃")
    
    print("┣━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━┫")
    print("┃          Вперед ▶️          ┃")
    print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    print("┃            📄 1 / 3            ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    
    print("\n🎯 KAMINSKYI EPIC - Сторінка 1/8:")
    print("┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓")
    
    # O*Translator перші 14 мов
    otrans_sample = [
        ("AF", "Afrikaans"), ("SQ", "Albanian"),
        ("AM", "Amharic"), ("AR", "🇸🇦 العربية"),
        ("HY", "Armenian"), ("AZ", "Azerbaijani"),
        ("EU", "Basque"), ("BE", "Belarusian"),
        ("BN", "Bengali"), ("BS", "Bosnian"),
        ("BG", "🇧🇬 Български"), ("CA", "Catalan"),
        ("ZH", "🇨🇳 中文"), ("CO", "Corsican")
    ]
    
    for i in range(0, 14, 2):
        left = otrans_sample[i][1][:17]
        if i + 1 < len(otrans_sample):
            right = otrans_sample[i+1][1][:17]
        else:
            right = ""
        print(f"┃ {left:17} ┃ {right:17} ┃")
    
    print("┣━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━┫")
    print("┃          Вперед ▶️          ┃")
    print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")  
    print("┃            📄 1 / 8            ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    
    print("\n✨ ОСОБЛИВОСТІ:")
    print("🔹 Автоматичний вибір мов залежно від обраної моделі")
    print("🔹 Пагінація для зручної навігації")
    print("🔹 Мови з прапорами країн для кращого розпізнавання")
    print("🔹 Сортування за алфавітом")
    print("🔹 Валідація підтримки мов перед перекладом")

if __name__ == "__main__":
    simulate_keyboard_layout()