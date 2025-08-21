from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging

logger = logging.getLogger(__name__)

# Helper функція для назв мов
LANGUAGE_NAMES = {
    "UK": "Українська",
    "EN": "English",
    "DE": "Deutsch",
    "FR": "Français",
    "ES": "Español",
    "PL": "Polski",
    "RU": "Русский",
    "ZH": "中文",
    "JA": "日本語"
}

def get_language_name(code):
    return LANGUAGE_NAMES.get(code, code)

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
        await state.update_data(source_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()
        
        # Показуємо вибрану мову
        lang_name = get_language_name(language_code)
        await callback.message.answer(f"✅ Вибрано мову оригіналу: {lang_name}")
        
        # Відправляємо вибір мови перекладу
        await callback.message.answer("<b>Крок 3/5:</b> Оберіть мову перекладу:", parse_mode="HTML")
        
        # Кнопки мов
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton("🇺🇦 UKR", callback_data="lang_UK"),
            types.InlineKeyboardButton("🇬🇧 ENG", callback_data="lang_EN"),
            types.InlineKeyboardButton("🇩🇪 GER", callback_data="lang_DE")
        )
        keyboard.add(
            types.InlineKeyboardButton("🇫🇷 FRA", callback_data="lang_FR"),
            types.InlineKeyboardButton("🇪🇸 SPA", callback_data="lang_ES"),
            types.InlineKeyboardButton("🇵🇱 POL", callback_data="lang_PL")
        )
        keyboard.add(
            types.InlineKeyboardButton("🇷🇺 RUS", callback_data="lang_RU"),
            types.InlineKeyboardButton("🇨🇳 CHN", callback_data="lang_ZH"),
            types.InlineKeyboardButton("🇯🇵 JPN", callback_data="lang_JA")
        )
        
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
        
        # Перевірка чи не однакові мови
        user_data = await state.get_data()
        source_lang = user_data.get('source_language')
        if source_lang and source_lang == language_code:
            await callback.message.answer("⚠️ Мови оригіналу та перекладу не можуть бути однаковими!")
            logger.warning(f"⚠️ ОДНАКОВІ МОВИ для користувача {callback.from_user.id}")
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
    
    logger.info("=== УСІ HANDLER'И LANGUAGE ЗАРЕЄСТРОВАНО ===")