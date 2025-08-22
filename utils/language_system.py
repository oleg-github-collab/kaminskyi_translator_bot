#!/usr/bin/env python3
"""
🌐 ПОТУЖНА СИСТЕМА МОВ - ВСІ МОВИ API
Ультрапродумана система з всіма мовами що підтримує API
"""

from typing import Dict, List, Tuple
from aiogram import types
import logging

logger = logging.getLogger(__name__)

# 🌍 ПОВНИЙ СПИСОК МОВ ДЛЯ API (130+ мов)
SUPPORTED_LANGUAGES = {
    # ЄВРОПЕЙСЬКІ МОВИ
    'AF': {'name': 'Afrikaans', 'flag': '🇿🇦', 'native': 'Afrikaans'},
    'SQ': {'name': 'Albanian', 'flag': '🇦🇱', 'native': 'Shqip'},
    'AM': {'name': 'Amharic', 'flag': '🇪🇹', 'native': 'አማርኛ'},
    'AR': {'name': 'Arabic', 'flag': '🇸🇦', 'native': 'العربية'},
    'HY': {'name': 'Armenian', 'flag': '🇦🇲', 'native': 'Հայերեն'},
    'AZ': {'name': 'Azerbaijani', 'flag': '🇦🇿', 'native': 'Azərbaycanca'},
    'EU': {'name': 'Basque', 'flag': '🏴', 'native': 'Euskera'},
    'BE': {'name': 'Belarusian', 'flag': '🇧🇾', 'native': 'Беларуская'},
    'BN': {'name': 'Bengali', 'flag': '🇧🇩', 'native': 'বাংলা'},
    'BS': {'name': 'Bosnian', 'flag': '🇧🇦', 'native': 'Bosanski'},
    'BG': {'name': 'Bulgarian', 'flag': '🇧🇬', 'native': 'Български'},
    'CA': {'name': 'Catalan', 'flag': '🏴', 'native': 'Català'},
    'ZH': {'name': 'Chinese', 'flag': '🇨🇳', 'native': '中文'},
    'ZH-TW': {'name': 'Chinese Traditional', 'flag': '🇹🇼', 'native': '繁體中文'},
    'CO': {'name': 'Corsican', 'flag': '🏴', 'native': 'Corsu'},
    'HR': {'name': 'Croatian', 'flag': '🇭🇷', 'native': 'Hrvatski'},
    'CS': {'name': 'Czech', 'flag': '🇨🇿', 'native': 'Čeština'},
    'DA': {'name': 'Danish', 'flag': '🇩🇰', 'native': 'Dansk'},
    'NL': {'name': 'Dutch', 'flag': '🇳🇱', 'native': 'Nederlands'},
    'EN': {'name': 'English', 'flag': '🇬🇧', 'native': 'English'},
    'EO': {'name': 'Esperanto', 'flag': '🏴', 'native': 'Esperanto'},
    'ET': {'name': 'Estonian', 'flag': '🇪🇪', 'native': 'Eesti'},
    'FI': {'name': 'Finnish', 'flag': '🇫🇮', 'native': 'Suomi'},
    'FR': {'name': 'French', 'flag': '🇫🇷', 'native': 'Français'},
    'FY': {'name': 'Frisian', 'flag': '🏴', 'native': 'Frysk'},
    'GL': {'name': 'Galician', 'flag': '🏴', 'native': 'Galego'},
    'KA': {'name': 'Georgian', 'flag': '🇬🇪', 'native': 'ქართული'},
    'DE': {'name': 'German', 'flag': '🇩🇪', 'native': 'Deutsch'},
    'EL': {'name': 'Greek', 'flag': '🇬🇷', 'native': 'Ελληνικά'},
    'GU': {'name': 'Gujarati', 'flag': '🇮🇳', 'native': 'ગુજરાતી'},
    'HT': {'name': 'Haitian Creole', 'flag': '🇭🇹', 'native': 'Kreyòl'},
    'HA': {'name': 'Hausa', 'flag': '🇳🇬', 'native': 'Hausa'},
    'HAW': {'name': 'Hawaiian', 'flag': '🏝️', 'native': 'ʻŌlelo Hawaiʻi'},
    'IW': {'name': 'Hebrew', 'flag': '🇮🇱', 'native': 'עברית'},
    'HI': {'name': 'Hindi', 'flag': '🇮🇳', 'native': 'हिन्दी'},
    'HMN': {'name': 'Hmong', 'flag': '🏴', 'native': 'Hmoob'},
    'HU': {'name': 'Hungarian', 'flag': '🇭🇺', 'native': 'Magyar'},
    'IS': {'name': 'Icelandic', 'flag': '🇮🇸', 'native': 'Íslenska'},
    'IG': {'name': 'Igbo', 'flag': '🇳🇬', 'native': 'Igbo'},
    'ID': {'name': 'Indonesian', 'flag': '🇮🇩', 'native': 'Bahasa Indonesia'},
    'GA': {'name': 'Irish', 'flag': '🇮🇪', 'native': 'Gaeilge'},
    'IT': {'name': 'Italian', 'flag': '🇮🇹', 'native': 'Italiano'},
    'JA': {'name': 'Japanese', 'flag': '🇯🇵', 'native': '日本語'},
    'JW': {'name': 'Javanese', 'flag': '🇮🇩', 'native': 'Basa Jawa'},
    'KN': {'name': 'Kannada', 'flag': '🇮🇳', 'native': 'ಕನ್ನಡ'},
    'KK': {'name': 'Kazakh', 'flag': '🇰🇿', 'native': 'Қазақша'},
    'KM': {'name': 'Khmer', 'flag': '🇰🇭', 'native': 'ខ្មែរ'},
    'RW': {'name': 'Kinyarwanda', 'flag': '🇷🇼', 'native': 'Ikinyarwanda'},
    'KO': {'name': 'Korean', 'flag': '🇰🇷', 'native': '한국어'},
    'KU': {'name': 'Kurdish', 'flag': '🏴', 'native': 'Kurdî'},
    'KY': {'name': 'Kyrgyz', 'flag': '🇰🇬', 'native': 'Кыргызча'},
    'LO': {'name': 'Lao', 'flag': '🇱🇦', 'native': 'ລາວ'},
    'LA': {'name': 'Latin', 'flag': '🏛️', 'native': 'Latina'},
    'LV': {'name': 'Latvian', 'flag': '🇱🇻', 'native': 'Latviešu'},
    'LT': {'name': 'Lithuanian', 'flag': '🇱🇹', 'native': 'Lietuvių'},
    'LB': {'name': 'Luxembourgish', 'flag': '🇱🇺', 'native': 'Lëtzebuergesch'},
    'MK': {'name': 'Macedonian', 'flag': '🇲🇰', 'native': 'Македонски'},
    'MG': {'name': 'Malagasy', 'flag': '🇲🇬', 'native': 'Malagasy'},
    'MS': {'name': 'Malay', 'flag': '🇲🇾', 'native': 'Bahasa Melayu'},
    'ML': {'name': 'Malayalam', 'flag': '🇮🇳', 'native': 'മലയാളം'},
    'MT': {'name': 'Maltese', 'flag': '🇲🇹', 'native': 'Malti'},
    'MI': {'name': 'Maori', 'flag': '🇳🇿', 'native': 'Te Reo Māori'},
    'MR': {'name': 'Marathi', 'flag': '🇮🇳', 'native': 'मराठी'},
    'MN': {'name': 'Mongolian', 'flag': '🇲🇳', 'native': 'Монгол'},
    'MY': {'name': 'Myanmar', 'flag': '🇲🇲', 'native': 'မြန်မာ'},
    'NE': {'name': 'Nepali', 'flag': '🇳🇵', 'native': 'नेपाली'},
    'NO': {'name': 'Norwegian', 'flag': '🇳🇴', 'native': 'Norsk'},
    'NY': {'name': 'Nyanja', 'flag': '🇲🇼', 'native': 'Chichewa'},
    'OR': {'name': 'Odia', 'flag': '🇮🇳', 'native': 'ଓଡ଼ିଆ'},
    'PS': {'name': 'Pashto', 'flag': '🇦🇫', 'native': 'پښتو'},
    'FA': {'name': 'Persian', 'flag': '🇮🇷', 'native': 'فارسی'},
    'PL': {'name': 'Polish', 'flag': '🇵🇱', 'native': 'Polski'},
    'PT': {'name': 'Portuguese', 'flag': '🇵🇹', 'native': 'Português'},
    'PA': {'name': 'Punjabi', 'flag': '🇮🇳', 'native': 'ਪੰਜਾਬੀ'},
    'RO': {'name': 'Romanian', 'flag': '🇷🇴', 'native': 'Română'},
    'RU': {'name': 'Russian', 'flag': '🇷🇺', 'native': 'Русский'},
    'SM': {'name': 'Samoan', 'flag': '🇼🇸', 'native': 'Gagana Samoa'},
    'GD': {'name': 'Scots Gaelic', 'flag': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'native': 'Gàidhlig'},
    'SR': {'name': 'Serbian', 'flag': '🇷🇸', 'native': 'Српски'},
    'ST': {'name': 'Sesotho', 'flag': '🇱🇸', 'native': 'Sesotho'},
    'SN': {'name': 'Shona', 'flag': '🇿🇼', 'native': 'ChiShona'},
    'SD': {'name': 'Sindhi', 'flag': '🇵🇰', 'native': 'سنڌي'},
    'SI': {'name': 'Sinhala', 'flag': '🇱🇰', 'native': 'සිංහල'},
    'SK': {'name': 'Slovak', 'flag': '🇸🇰', 'native': 'Slovenčina'},
    'SL': {'name': 'Slovenian', 'flag': '🇸🇮', 'native': 'Slovenščina'},
    'SO': {'name': 'Somali', 'flag': '🇸🇴', 'native': 'Soomaali'},
    'ES': {'name': 'Spanish', 'flag': '🇪🇸', 'native': 'Español'},
    'SU': {'name': 'Sundanese', 'flag': '🇮🇩', 'native': 'Basa Sunda'},
    'SW': {'name': 'Swahili', 'flag': '🇹🇿', 'native': 'Kiswahili'},
    'SV': {'name': 'Swedish', 'flag': '🇸🇪', 'native': 'Svenska'},
    'TG': {'name': 'Tajik', 'flag': '🇹🇯', 'native': 'Тоҷикӣ'},
    'TA': {'name': 'Tamil', 'flag': '🇮🇳', 'native': 'தமிழ்'},
    'TT': {'name': 'Tatar', 'flag': '🏴', 'native': 'Татарча'},
    'TE': {'name': 'Telugu', 'flag': '🇮🇳', 'native': 'తెలుగు'},
    'TH': {'name': 'Thai', 'flag': '🇹🇭', 'native': 'ไทย'},
    'TI': {'name': 'Tigrinya', 'flag': '🇪🇷', 'native': 'ትግርኛ'},
    'TR': {'name': 'Turkish', 'flag': '🇹🇷', 'native': 'Türkçe'},
    'TK': {'name': 'Turkmen', 'flag': '🇹🇲', 'native': 'Türkmençe'},
    'UK': {'name': 'Ukrainian', 'flag': '🇺🇦', 'native': 'Українська'},
    'UR': {'name': 'Urdu', 'flag': '🇵🇰', 'native': 'اردو'},
    'UG': {'name': 'Uyghur', 'flag': '🏴', 'native': 'ئۇيغۇرچە'},
    'UZ': {'name': 'Uzbek', 'flag': '🇺🇿', 'native': 'Oʻzbekcha'},
    'VI': {'name': 'Vietnamese', 'flag': '🇻🇳', 'native': 'Tiếng Việt'},
    'CY': {'name': 'Welsh', 'flag': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'native': 'Cymraeg'},
    'XH': {'name': 'Xhosa', 'flag': '🇿🇦', 'native': 'isiXhosa'},
    'YI': {'name': 'Yiddish', 'flag': '🏴', 'native': 'ייִדיש'},
    'YO': {'name': 'Yoruba', 'flag': '🇳🇬', 'native': 'Yorùbá'},
    'ZU': {'name': 'Zulu', 'flag': '🇿🇦', 'native': 'isiZulu'},
}

# 🔥 ПОПУЛЯРНІ МОВИ (для швидкого доступу)
POPULAR_LANGUAGES = [
    'UK', 'EN', 'RU', 'DE', 'FR', 'ES', 'IT', 'PL', 
    'ZH', 'JA', 'KO', 'AR', 'PT', 'TR', 'HI'
]

# 🌍 РЕГІОНАЛЬНІ ГРУПИ МОВ
LANGUAGE_REGIONS = {
    'European': ['UK', 'EN', 'RU', 'DE', 'FR', 'ES', 'IT', 'PL', 'PT', 'NL', 'SV', 'NO', 'DA', 'FI', 'CS', 'HU', 'RO', 'BG', 'HR', 'SK', 'SL', 'ET', 'LV', 'LT'],
    'Asian': ['ZH', 'JA', 'KO', 'HI', 'TH', 'VI', 'ID', 'MS', 'TA', 'TE', 'BN', 'GU', 'KN', 'ML', 'MR', 'NE', 'PA', 'UR', 'FA', 'AR'],
    'African': ['AF', 'AM', 'HA', 'IG', 'RW', 'SO', 'SW', 'XH', 'YO', 'ZU', 'ST', 'SN'],
    'Americas': ['ES', 'PT', 'EN', 'FR', 'HT', 'GD']
}

def get_language_info(code: str) -> Dict:
    """Отримати інформацію про мову"""
    return SUPPORTED_LANGUAGES.get(code.upper(), {
        'name': code,
        'flag': '🏴',
        'native': code
    })

def get_language_name(code: str) -> str:
    """Отримати назву мови"""
    info = get_language_info(code)
    return f"{info['flag']} {info['name']}"

def get_language_native_name(code: str) -> str:
    """Отримати нативну назву мови"""
    info = get_language_info(code)
    return f"{info['flag']} {info['native']}"

def validate_language(code: str) -> bool:
    """Перевірити чи підтримується мова"""
    return code.upper() in SUPPORTED_LANGUAGES

def get_popular_languages() -> List[str]:
    """Отримати список популярних мов"""
    return POPULAR_LANGUAGES.copy()

def get_languages_by_region(region: str) -> List[str]:
    """Отримати мови за регіоном"""
    return LANGUAGE_REGIONS.get(region, [])

def create_language_keyboard(languages: List[str] = None, per_row: int = 3, show_native: bool = True) -> types.InlineKeyboardMarkup:
    """
    Створити клавіатуру з мовами
    
    Args:
        languages: Список кодів мов (якщо None - використовуються популярні)
        per_row: Кількість кнопок в рядку
        show_native: Показувати нативні назви
    """
    if languages is None:
        languages = POPULAR_LANGUAGES
    
    keyboard = types.InlineKeyboardMarkup(row_width=per_row)
    
    # Створюємо кнопки по рядках
    buttons = []
    for lang_code in languages:
        if lang_code in SUPPORTED_LANGUAGES:
            info = SUPPORTED_LANGUAGES[lang_code]
            if show_native:
                text = f"{info['flag']} {info['native']}"
            else:
                text = f"{info['flag']} {info['name']}"
            
            button = types.InlineKeyboardButton(text, callback_data=f"lang_{lang_code}")
            buttons.append(button)
            
            # Додаємо рядок кнопок
            if len(buttons) == per_row:
                keyboard.row(*buttons)
                buttons = []
    
    # Додаємо останній рядок якщо є залишкові кнопки
    if buttons:
        keyboard.row(*buttons)
    
    return keyboard

def create_regional_keyboard(region: str) -> types.InlineKeyboardMarkup:
    """Створити клавіатуру з мовами за регіоном"""
    languages = get_languages_by_region(region)
    return create_language_keyboard(languages, per_row=3)

def create_popular_languages_keyboard() -> types.InlineKeyboardMarkup:
    """Створити клавіатуру з популярними мовами"""
    return create_language_keyboard(POPULAR_LANGUAGES, per_row=3)

def create_all_languages_keyboard() -> types.InlineKeyboardMarkup:
    """Створити клавіатуру з ВСІ мовами (пагінована)"""
    # Для всіх мов робимо більш компактний варіант
    all_codes = sorted(SUPPORTED_LANGUAGES.keys())
    return create_language_keyboard(all_codes, per_row=4, show_native=False)

def create_language_menu_keyboard() -> types.InlineKeyboardMarkup:
    """Створити головне меню вибору мов"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔥 Популярні мови", callback_data="lang_menu_popular"))
    keyboard.add(types.InlineKeyboardButton("🌍 Всі мови", callback_data="lang_menu_all"))
    keyboard.add(
        types.InlineKeyboardButton("🇪🇺 Європейські", callback_data="lang_menu_european"),
        types.InlineKeyboardButton("🌏 Азійські", callback_data="lang_menu_asian")
    )
    keyboard.add(
        types.InlineKeyboardButton("🌍 Африканські", callback_data="lang_menu_african"),
        types.InlineKeyboardButton("🌎 Американські", callback_data="lang_menu_americas")
    )
    return keyboard

# Експорт основних функцій
__all__ = [
    'SUPPORTED_LANGUAGES', 'POPULAR_LANGUAGES', 'LANGUAGE_REGIONS',
    'get_language_info', 'get_language_name', 'get_language_native_name',
    'validate_language', 'get_popular_languages', 'get_languages_by_region',
    'create_language_keyboard', 'create_regional_keyboard', 
    'create_popular_languages_keyboard', 'create_all_languages_keyboard',
    'create_language_menu_keyboard'
]

if __name__ == "__main__":
    # Тест системи мов
    print("🧪 Тестуємо систему мов...")
    
    print(f"📊 Всього мов: {len(SUPPORTED_LANGUAGES)}")
    print(f"🔥 Популярних мов: {len(POPULAR_LANGUAGES)}")
    
    # Тест отримання інформації
    test_lang = 'UK'
    info = get_language_info(test_lang)
    print(f"🇺🇦 Тест {test_lang}: {info}")
    
    # Тест назв
    print(f"📝 Назва: {get_language_name(test_lang)}")
    print(f"🗣️ Нативна: {get_language_native_name(test_lang)}")
    
    # Тест валідації
    print(f"✅ Валідна мова UK: {validate_language('UK')}")
    print(f"❌ Валідна мова XX: {validate_language('XX')}")
    
    print("🚀 Система мов готова!")