from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging

logger = logging.getLogger(__name__)

# Імпорт мов з конфігурації
from config import COMMON_LANGUAGES, DEEPL_LANGUAGES, OTRANSLATOR_LANGUAGES

def get_language_name(code):
    """Отримати назву мови за кодом"""
    return COMMON_LANGUAGES.get(code, DEEPL_LANGUAGES.get(code, OTRANSLATOR_LANGUAGES.get(code, code)))

def get_supported_languages(model="basic"):
    """Отримати підтримувані мови для конкретної моделі"""
    if model == "basic":
        return DEEPL_LANGUAGES
    elif model == "epic":
        return OTRANSLATOR_LANGUAGES
    else:
        return COMMON_LANGUAGES

def create_language_keyboard(model="basic", max_per_page=20, page=0):
    """Створити клавіатуру з мовами з підтримкою пагінації"""
    languages = get_supported_languages(model)
    
    # Використовуємо COMMON_LANGUAGES для відображення з прапорами
    display_languages = []
    for code in languages.keys():
        display_name = COMMON_LANGUAGES.get(code, languages[code])
        display_languages.append((code, display_name))
    
    # Сортування за назвою
    display_languages.sort(key=lambda x: x[1])
    
    # Пагінація
    start_idx = page * max_per_page
    end_idx = start_idx + max_per_page
    page_languages = display_languages[start_idx:end_idx]
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Додаємо кнопки мов
    for i in range(0, len(page_languages), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(page_languages):
                code, name = page_languages[i + j]
                # Обрізаємо довгі назви для кнопок
                button_text = name if len(name) <= 20 else name[:17] + "..."
                row_buttons.append(types.InlineKeyboardButton(button_text, callback_data=f"lang_{code}"))
        keyboard.row(*row_buttons)
    
    # Кнопки навігації
    if len(display_languages) > max_per_page:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"lang_page_{page-1}"))
        if end_idx < len(display_languages):
            nav_buttons.append(types.InlineKeyboardButton("Далі ➡️", callback_data=f"lang_page_{page+1}"))
        if nav_buttons:
            keyboard.row(*nav_buttons)
    
    return keyboard

async def choose_source_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ОРИГІНАЛУ"""
    try:
        logger.info(f"🔵 ВИБІР МОВИ ОРИГІНАЛУ: {callback.data} для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data or not callback.data.startswith("lang_"):
            logger.warning(f"⚠️ Неправильні дані від користувача {callback.from_user.id}: {callback.data}")
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        
        # Отримуємо мову
        language_code = callback.data.split("_")[1]
        
        # Валідація підтримки мови для вибраної моделі
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        
        supported_languages = get_supported_languages(model)
        if language_code not in supported_languages:
            await callback.message.answer(f"⚠️ Мова {get_language_name(language_code)} не підтримується моделлю {model}")
            logger.warning(f"⚠️ НЕПІДТРИМУВАНА МОВА {language_code} для моделі {model}")
            return
        
        await state.update_data(source_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()
        
        # Показуємо вибрану мову
        lang_name = get_language_name(language_code)
        await callback.message.answer(f"✅ Вибрано мову оригіналу: {lang_name}")
        
        # Відправляємо вибір мови перекладу
        await callback.message.answer("<b>Крок 3/5:</b> Оберіть мову перекладу:", parse_mode="HTML")
        
        # Отримуємо модель та створюємо відповідну клавіатуру
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        keyboard = create_language_keyboard(model)
        
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        logger.info(f"✅ МОВА ОРИГІНАЛУ {language_code} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в choose_source_language для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ПЕРЕКЛАДУ"""
    try:
        logger.info(f"🔵 ВИБІР МОВИ ПЕРЕКЛАДУ: {callback.data} для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data or not callback.data.startswith("lang_"):
            logger.warning(f"⚠️ Неправильні дані від користувача {callback.from_user.id}: {callback.data}")
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        
        # Отримуємо мову
        language_code = callback.data.split("_")[1]
        
        # Перевірка чи не однакові мови та валідація підтримки
        user_data = await state.get_data()
        source_lang = user_data.get('source_language')
        model = user_data.get('model', 'basic')
        
        if source_lang and source_lang == language_code:
            await callback.message.answer("⚠️ Мови оригіналу та перекладу не можуть бути однаковими!")
            logger.warning(f"⚠️ ОДНАКОВІ МОВИ для користувача {callback.from_user.id}")
            return
        
        # Валідація підтримки мови для вибраної моделі
        supported_languages = get_supported_languages(model)
        if language_code not in supported_languages:
            await callback.message.answer(f"⚠️ Мова {get_language_name(language_code)} не підтримується моделлю {model}")
            logger.warning(f"⚠️ НЕПІДТРИМУВАНА МОВА {language_code} для моделі {model}")
            return
        
        await state.update_data(target_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()
        
        # Показуємо вибрану мову
        lang_name = get_language_name(language_code)
        await callback.message.answer(f"✅ Вибрано мову перекладу: {lang_name}")
        
        # Відправляємо запит на файл
        await callback.message.answer("<b>Крок 4/5:</b> Надішліть файл для перекладу (txt, docx, pdf)", parse_mode="HTML")
        
        logger.info(f"✅ МОВА ПЕРЕКЛАДУ {language_code} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в choose_target_language для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def handle_language_pagination(callback: types.CallbackQuery, state: FSMContext):
    """Обробка пагінації мов"""
    try:
        await callback.answer()
        
        # Отримуємо номер сторінки
        page = int(callback.data.split("_")[-1])
        
        # Отримуємо поточні дані
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        
        # Створюємо нову клавіатуру
        keyboard = create_language_keyboard(model, page=page)
        
        # Оновлюємо повідомлення
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_language_pagination: {str(e)}")
        await callback.answer("⚠️ Помилка")

def register_handlers_language(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ МОВ З ПРАВИЛЬНИМИ ФІЛЬТРАМИ"""
    logger.info("=== РЕЄСТРАЦІЯ HANDLER'ІВ LANGUAGE ===")
    
    # Handler для вибору мови оригіналу (стан waiting_for_source_language)
    dp.register_callback_query_handler(
        choose_source_language,
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_source_language
    )
    logger.info("✅ Зареєстровано choose_source_language")
    
    # Handler для вибору мови перекладу (стан waiting_for_target_language)
    dp.register_callback_query_handler(
        choose_target_language,
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_target_language
    )
    logger.info("✅ Зареєстровано choose_target_language")
    
    # Handler для пагінації мов
    dp.register_callback_query_handler(
        handle_language_pagination,
        lambda c: c.data and c.data.startswith("lang_page_"),
        state=[TranslationStates.waiting_for_source_language, TranslationStates.waiting_for_target_language]
    )
    logger.info("✅ Зареєстровано handle_language_pagination")
    
    logger.info("=== УСІ HANDLER'И LANGUAGE ЗАРЕЄСТРОВАНО ===")