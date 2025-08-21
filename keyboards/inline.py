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
    """Клавіатура продовження роботи"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 Новий переклад", callback_data="continue_translate"),
        InlineKeyboardButton("📥 Завантажити файл", callback_data="upload_file")
    )
    keyboard.add(
        InlineKeyboardButton("📊 Мої переклади", callback_data="my_translations"),
        InlineKeyboardButton("⚙️ Налаштування", callback_data="settings")
    )
    keyboard.add(InlineKeyboardButton("📞 Підтримка", callback_data="contact_support"))
    return keyboard

def get_payment_keyboard(amount: float = None, model: str = None):
    """Розширена клавіатура оплати"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    payment_text = f"💳 Сплатити {amount}€" if amount else "💳 Оплатити"
    keyboard.add(InlineKeyboardButton(payment_text, callback_data="process_payment"))
    
    keyboard.add(InlineKeyboardButton("📊 Детальна інформація", callback_data="payment_details"))
    keyboard.add(InlineKeyboardButton("❓ Як відбувається оплата?", callback_data="payment_help"))
    keyboard.add(InlineKeyboardButton("🔄 Вибрати інший файл", callback_data="upload_another"))
    keyboard.add(InlineKeyboardButton("⚙️ Змінити модель", callback_data="change_model"))
    
    return keyboard

def get_file_action_keyboard(file_info: dict = None):
    """Клавіатура дій з файлом з детальною інформацією"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    if file_info and file_info.get('amount'):
        keyboard.add(InlineKeyboardButton(f"💳 Сплатити {file_info['amount']}€", callback_data="process_payment"))
    else:
        keyboard.add(InlineKeyboardButton("💳 Перейти до оплати", callback_data="process_payment"))
    
    keyboard.add(InlineKeyboardButton("📊 Переглянути деталі", callback_data="file_details"))
    keyboard.add(InlineKeyboardButton("⚙️ Змінити модель", callback_data="change_model"))
    keyboard.add(InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
    keyboard.add(InlineKeyboardButton("❓ Допомога", callback_data="help"))
    
    return keyboard

def get_payment_action_keyboard():
    """Клавіатура дій після оплати"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🚀 Почати переклад", callback_data="start_translation"))
    keyboard.add(InlineKeyboardButton("🧾 Переглянути чек", callback_data="view_receipt"))
    keyboard.add(InlineKeyboardButton("🔄 Новий переклад", callback_data="upload_another"))
    keyboard.add(InlineKeyboardButton("📞 Підтримка", callback_data="contact_support"))
    return keyboard