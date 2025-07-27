from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging
from utils.translate_utils import fetch_deepl_languages, fetch_otranslator_languages

logger = logging.getLogger(__name__)

# Languages will be fetched from APIs
LANGUAGE_NAMES = {}
LANGUAGE_NAMES.update(fetch_deepl_languages())
LANGUAGE_NAMES.update(fetch_otranslator_languages())

# Fallback minimal set if APIs fail
if not LANGUAGE_NAMES:
    LANGUAGE_NAMES = {
        "UK": "Українська",
        "EN": "English",
        "DE": "Deutsch",
        "FR": "Français",
        "ES": "Español",
        "PL": "Polski",
        "RU": "Русский",
        "ZH": "中文",
        "JA": "日本語",
    }

def get_language_name(code):
    return LANGUAGE_NAMES.get(code, code)


def build_language_keyboard() -> types.InlineKeyboardMarkup:
    """Створює клавіатуру з усіма доступними мовами"""
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for code, name in LANGUAGE_NAMES.items():
        keyboard.insert(types.InlineKeyboardButton(name, callback_data=f"lang_{code}"))
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
        await state.update_data(source_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()
        
        # Показуємо вибрану мову
        lang_name = get_language_name(language_code)
        await callback.message.answer(f"✅ Вибрано мову оригіналу: {lang_name}")
        
        # Відправляємо вибір мови перекладу
        await callback.message.answer("<b>Крок 3/5:</b> Оберіть мову перекладу:", parse_mode="HTML")
        
        # Кнопки мов
        keyboard = build_language_keyboard()
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
    """РЕЄСТРАЦІЯ HANDLER'ІВ МОВ"""
    dp.register_callback_query_handler(
        choose_source_language,
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_source_language,
    )
    dp.register_callback_query_handler(
        choose_target_language,
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_target_language,
    )