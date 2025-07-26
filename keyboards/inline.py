from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DEEPL_LANGUAGES, MODELS

def get_model_keyboard(user_lang: str = "en"):
    """Клавіатура вибору моделі перекладу"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
        InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
    )
    return keyboard

def get_language_keyboard():
    """Клавіатура вибору мови"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    # Основні мови для тестування
    keyboard.add(
        InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_UK"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_EN")
    )
    keyboard.add(
        InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_DE"),
        InlineKeyboardButton("🇫🇷 Français", callback_data="lang_FR")
    )
    keyboard.add(
        InlineKeyboardButton("🇪🇸 Español", callback_data="lang_ES"),
        InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_PL")
    )
    return keyboard

def get_continue_keyboard(user_lang: str = "en"):
    """Клавіатура продовження"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 Новий переклад", callback_data="continue_translate"),
        InlineKeyboardButton("👋 Вийти", callback_data="exit")
    )
    return keyboard