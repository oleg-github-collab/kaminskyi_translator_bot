from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DEEPL_LANGUAGES, OTRANSLATOR_LANGUAGES, ALL_LANGUAGES_WITH_FLAGS, MODELS

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
    
    # 1. ВИБІР МОВ ЗАЛЕЖНО ВІД МОДЕЛІ
    if model == "basic":
        available_languages = DEEPL_LANGUAGES
    elif model == "epic":
        available_languages = OTRANSLATOR_LANGUAGES
    else:
        available_languages = ALL_LANGUAGES_WITH_FLAGS
    
    # 2. СТВОРЕННЯ СПИСКУ З ПРАПОРАМИ
    language_list = []
    for lang_code, lang_name in available_languages.items():
        # Використовуємо красиву назву з прапором для ВСІ мов
        display_name = ALL_LANGUAGES_WITH_FLAGS.get(lang_code, lang_name)
        language_list.append((lang_code, display_name))
    
    # 3. СОРТУВАННЯ ЗА АЛФАВІТОМ
    language_list.sort(key=lambda x: x[1])
    
    # 4. ПАГІНАЦІЯ
    languages_per_page = 12  # 6 рядків по 2 мови
    total_languages = len(language_list)
    total_pages = (total_languages + languages_per_page - 1) // languages_per_page
    
    # Обмежуємо сторінку
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1 if total_pages > 0 else 0
    
    # Отримуємо мови для поточної сторінки
    start_index = page * languages_per_page
    end_index = min(start_index + languages_per_page, total_languages)
    current_page_languages = language_list[start_index:end_index]
    
    # 5. СТВОРЕННЯ КЛАВІАТУРИ
    keyboard = InlineKeyboardMarkup()
    
    # Додаємо кнопки мов по 2 в рядку
    for i in range(0, len(current_page_languages), 2):
        row = []
        
        # Перша мова в рядку
        lang_code, lang_name = current_page_languages[i]
        button_text = lang_name[:18] + "..." if len(lang_name) > 18 else lang_name
        row.append(InlineKeyboardButton(button_text, callback_data=f"lang_{lang_code}"))
        
        # Друга мова в рядку (якщо є)
        if i + 1 < len(current_page_languages):
            lang_code, lang_name = current_page_languages[i + 1]
            button_text = lang_name[:18] + "..." if len(lang_name) > 18 else lang_name
            row.append(InlineKeyboardButton(button_text, callback_data=f"lang_{lang_code}"))
        
        keyboard.row(*row)
    
    # 6. НАВІГАЦІЙНІ КНОПКИ
    if total_pages > 1:
        nav_row = []
        
        # Кнопка "Назад"
        if page > 0:
            nav_row.append(InlineKeyboardButton("◀️ Назад", callback_data=f"lang_page_{page-1}"))
        
        # Кнопка "Вперед"  
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"lang_page_{page+1}"))
        
        if nav_row:
            keyboard.row(*nav_row)
        
        # Індикатор сторінки
        page_info = f"📄 Сторінка {page + 1} з {total_pages} • {total_languages} мов"
        keyboard.row(InlineKeyboardButton(page_info, callback_data="page_info"))
    
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