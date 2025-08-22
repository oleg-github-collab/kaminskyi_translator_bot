from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DEEPL_LANGUAGES, OTRANSLATOR_LANGUAGES, COMMON_LANGUAGES, MODELS

def get_model_keyboard(user_lang: str = "en"):
    """Клавіатура вибору моделі перекладу"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
        InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
    )
    return keyboard

def get_language_keyboard(model="basic", page=0):
    """Клавіатура вибору мови з повним списком та пагінацією"""
    # Вибираємо мови залежно від моделі
    if model == "basic":
        languages = DEEPL_LANGUAGES
    elif model == "epic":
        languages = OTRANSLATOR_LANGUAGES
    else:
        languages = COMMON_LANGUAGES
    
    # Конвертуємо в список для сортування
    lang_list = []
    for code, name in languages.items():
        # Використовуємо назву з прапором якщо є в COMMON_LANGUAGES
        display_name = COMMON_LANGUAGES.get(code, name)
        lang_list.append((code, display_name))
    
    # Сортуємо за назвою
    lang_list.sort(key=lambda x: x[1])
    
    # Пагінація - 14 мов на сторінку (7 рядків по 2)
    per_page = 14
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_languages = lang_list[start_idx:end_idx]
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Створюємо кнопки по 2 в рядку
    for i in range(0, len(page_languages), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(page_languages):
                code, name = page_languages[i + j]
                # Обрізаємо назву якщо довга
                if len(name) > 20:
                    button_text = name[:17] + "..."
                else:
                    button_text = name
                row_buttons.append(InlineKeyboardButton(button_text, callback_data=f"lang_{code}"))
        
        if len(row_buttons) == 2:
            keyboard.row(row_buttons[0], row_buttons[1])
        elif len(row_buttons) == 1:
            keyboard.row(row_buttons[0])
    
    # Навігаційні кнопки якщо потрібно
    total_pages = (len(lang_list) + per_page - 1) // per_page
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"lang_page_{page-1}"))
        if page + 1 < total_pages:
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"lang_page_{page+1}"))
        
        if nav_buttons:
            keyboard.row(*nav_buttons)
        
        # Показуємо номер сторінки
        keyboard.row(InlineKeyboardButton(f"📄 {page + 1} / {total_pages}", callback_data="page_info"))
    
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