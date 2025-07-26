from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DEEPL_LANGUAGES, MODELS

# Іконки прапорів для мов
FLAG_ICONS = {
    "BG": "🇧🇬", "CS": "🇨🇿", "DA": "🇩🇰", "DE": "🇩🇪", "EL": "🇬🇷",
    "EN": "🇬🇧", "ES": "🇪🇸", "ET": "🇪🇪", "FI": "🇫🇮", "FR": "🇫🇷",
    "HU": "🇭🇺", "ID": "🇮🇩", "IT": "🇮🇹", "JA": "🇯🇵", "KO": "🇰🇷",
    "LT": "🇱🇹", "LV": "🇱🇻", "NB": "🇳🇴", "NL": "🇳🇱", "PL": "🇵🇱",
    "PT": "🇵🇹", "RO": "🇷🇴", "RU": "🇷🇺", "SK": "🇸🇰", "SL": "🇸🇮",
    "SV": "🇸🇪", "TR": "🇹🇷", "UK": "🇺🇦", "ZH": "🇨🇳"
}

def get_model_keyboard(user_lang: str = "en"):
    """Клавіатура вибору моделі перекладу"""
    texts = {
        "uk": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "en": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "de": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "fr": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "es": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"}
    }
    
    lang_texts = texts.get(user_lang, texts["en"])
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=lang_texts["basic"], callback_data="model_basic"),
        InlineKeyboardButton(text=lang_texts["epic"], callback_data="model_epic")
    )
    return keyboard

def get_language_keyboard():
    """Клавіатура вибору мови з іконками прапорів"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    sorted_languages = sorted(FLAG_ICONS.items())
    
    for i in range(0, len(sorted_languages), 2):
        row_buttons = []
        # Перша мова в рядку
        if i < len(sorted_languages):
            code, _ = sorted_languages[i]
            language_name = DEEPL_LANGUAGES.get(code, code)
            flag_icon = FLAG_ICONS.get(code, "🏳️")
            row_buttons.append(InlineKeyboardButton(text=f"{flag_icon} {language_name}", callback_data=f"lang_{code}"))
        # Друга мова в рядку
        if i + 1 < len(sorted_languages):
            code, _ = sorted_languages[i + 1]
            language_name = DEEPL_LANGUAGES.get(code, code)
            flag_icon = FLAG_ICONS.get(code, "🏳️")
            row_buttons.append(InlineKeyboardButton(text=f"{flag_icon} {language_name}", callback_data=f"lang_{code}"))
        
        if row_buttons:
            keyboard.row(*row_buttons)
    
    return keyboard

def get_continue_keyboard(user_lang: str = "en"):
    """Клавіатура продовження роботи"""
    texts = {
        "uk": {"continue": "🔄 Новий переклад", "exit": "👋 Вийти"},
        "en": {"continue": "🔄 New translation", "exit": "👋 Exit"},
        "de": {"continue": "🔄 Neue Übersetzung", "exit": "👋 Beenden"},
        "fr": {"continue": "🔄 Nouvelle traduction", "exit": "👋 Quitter"},
        "es": {"continue": "🔄 Nueva traducción", "exit": "👋 Salir"}
    }
    
    lang_texts = texts.get(user_lang, texts["en"])
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text=lang_texts["continue"], callback_data="continue_translate"),
        InlineKeyboardButton(text=lang_texts["exit"], callback_data="exit")
    )
    return keyboard

def get_file_action_keyboard():
    """Клавіатура дій з файлом"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
    keyboard.add(InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
    return keyboard

def get_payment_action_keyboard():
    """Клавіатура після оплати"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("✅ Продовжити", callback_data="payment_done"))
    keyboard.add(InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
    return keyboard

# ДОДАНО ВІДСУТНЮ ФУНКЦІЮ
def get_payment_keyboard():
    """Клавіатура оплати (для сумісності)"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
    keyboard.add(InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
    return keyboard