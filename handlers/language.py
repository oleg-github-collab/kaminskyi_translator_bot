from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging
from utils.translate_utils import (
    fetch_deepl_languages,
    fetch_otranslator_languages,
)
import math

logger = logging.getLogger(__name__)

# Languages will be fetched from APIs
LANGUAGE_NAMES = {}
LANGUAGE_NAMES.update(fetch_deepl_languages())
LANGUAGE_NAMES.update(fetch_otranslator_languages())

LANGUAGE_CODES = sorted(LANGUAGE_NAMES.keys())
LANGUAGES_PER_PAGE = 9

# Map language codes to appropriate flag codes
FLAG_OVERRIDES = {
    "EN": "US",  # show US flag for English
    "UK": "UA",  # Ukrainian
    "BE": "BY",  # Belarusian
    "CS": "CZ",
    "DA": "DK",
    "EL": "GR",
    "NB": "NO",
    "SR": "RS",

    "UK": "UA",   # Ukrainian
    "PT": "PT",
    "PT-BR": "BR",
    "ZH": "CN",
    "JA": "JP",
    "KO": "KR",
    "AR": "SA",
    "HE": "IL",
    "HI": "IN",
    "VI": "VN",
    "KA": "GE",
    "KK": "KZ",
}

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
    LANGUAGE_CODES = sorted(LANGUAGE_NAMES.keys())

def get_language_name(code):
    return LANGUAGE_NAMES.get(code, code)


def get_flag(code: str) -> str:
    """Return emoji flag for language code"""

    code_up = code.upper()
    # Try full code override first, then base ISO code
    flag_code = FLAG_OVERRIDES.get(code_up)
    if not flag_code:
        base_code = code_up.split("-")[0]
        flag_code = FLAG_OVERRIDES.get(base_code, base_code)
    if len(flag_code) == 2 and flag_code.isalpha():
        base = 0x1F1E6
        return chr(base + ord(flag_code[0]) - 65) + chr(base + ord(flag_code[1]) - 65)
    base_code = code.split("-")[0].upper()
    flag_code = FLAG_OVERRIDES.get(base_code, base_code)
    if len(flag_code) == 2 and flag_code.isalpha():
        base = 0x1F1E6
        return chr(base + ord(flag_code[0]) - 65) + chr(base + ord(flag_code[1]) - 65)


    code = code.split("-")[0].upper()
    if len(code) == 2 and code.isalpha():
        base = 0x1F1E6
        return chr(base + ord(code[0]) - 65) + chr(base + ord(code[1]) - 65)
    code = code.split("-")[0]
    if len(code) == 2:
        return chr(0x1F1E6 + ord(code[0].upper()) - 65) + chr(0x1F1E6 + ord(code[1].upper()) - 65)

    return ""


def build_language_keyboard() -> types.InlineKeyboardMarkup:
    """Клавіатура мов для першої сторінки"""
    return build_language_keyboard_page(0)


def build_language_keyboard_page(page: int) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    subset = LANGUAGE_CODES[page * LANGUAGES_PER_PAGE:(page + 1) * LANGUAGES_PER_PAGE]
    for code in subset:
        name = LANGUAGE_NAMES[code]
        flag = get_flag(code)
        keyboard.insert(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"lang_{code}"))

    total_pages = int(math.ceil(len(LANGUAGE_CODES) / LANGUAGES_PER_PAGE))
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"langpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"langpage_{page+1}"))
    if nav_buttons:
        keyboard.row(*nav_buttons)
    return keyboard


async def switch_language_page(callback: types.CallbackQuery, state: FSMContext):
    """Перемикання сторінок мов"""
    await callback.answer()
    page = int(callback.data.split("_")[1])
    keyboard = build_language_keyboard_page(page)
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except Exception:
        await callback.message.reply("Виберіть мову:", reply_markup=keyboard)

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
    dp.register_callback_query_handler(
        switch_language_page,
        lambda c: c.data and c.data.startswith("langpage_"),
        state=TranslationStates.waiting_for_source_language,
    )
    dp.register_callback_query_handler(
        switch_language_page,
        lambda c: c.data and c.data.startswith("langpage_"),
        state=TranslationStates.waiting_for_target_language,
    )
