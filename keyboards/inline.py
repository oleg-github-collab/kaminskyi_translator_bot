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

# ДОДАНО ВІДСУТНЮ ФУНКЦІЮ
def get_payment_keyboard():
    """Клавіатура оплати"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
    keyboard.add(InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
    return keyboard

# ДОДАНО ВІДСУТНЮ ФУНКЦІЮ
def get_file_action_keyboard():
    """Клавіатура дій з файлом"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
    keyboard.add(InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
    return keyboard

# ДОДАНО ВІДСУТНЮ ФУНКЦІЮ
def get_payment_action_keyboard():
    """Клавіатура після оплати"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("✅ Продовжити", callback_data="payment_done"))
    keyboard.add(InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
    return keyboard