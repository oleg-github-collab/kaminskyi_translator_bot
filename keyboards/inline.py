from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DEEPL_LANGUAGES, MODELS

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
    """Клавіатура вибору мови"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []
    sorted_languages = sorted(DEEPL_LANGUAGES.items())
    
    for i in range(0, len(sorted_languages), 2):
        row_buttons = []
        if i < len(sorted_languages):
            code1, name1 = sorted_languages[i]
            row_buttons.append(InlineKeyboardButton(text=name1, callback_data=f"lang_{code1}"))
        if i + 1 < len(sorted_languages):
            code2, name2 = sorted_languages[i + 1]
            row_buttons.append(InlineKeyboardButton(text=name2, callback_data=f"lang_{code2}"))
        
        if row_buttons:
            keyboard.row(*row_buttons)
    
    return keyboard

def get_continue_keyboard(user_lang: str = "en"):
    """Клавіатура продовження роботи"""
    texts = {
        "uk": {"continue": "Продовжити переклад", "exit": "Вийти"},
        "en": {"continue": "Continue translation", "exit": "Exit"},
        "de": {"continue": "Übersetzung fortsetzen", "exit": "Beenden"},
        "fr": {"continue": "Continuer la traduction", "exit": "Quitter"},
        "es": {"continue": "Continuar traducción", "exit": "Salir"}
    }
    
    lang_texts = texts.get(user_lang, texts["en"])
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=lang_texts["continue"], callback_data="continue_translate"),
        InlineKeyboardButton(text=lang_texts["exit"], callback_data="exit")
    )
    return keyboard

def get_payment_keyboard():
    """Клавіатура оплати"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
    return keyboard

def get_file_action_keyboard():
    """Клавіатура дій з файлом"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
    keyboard.add(InlineKeyboardButton("🔄 Завантажити інший файл", callback_data="upload_another"))
    return keyboard