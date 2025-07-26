from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging

logger = logging.getLogger(__name__)

# Helper функція для отримання назви мови
def _get_language_name(lang_code):
    """Отримання назви мови за кодом"""
    languages = {
        "UK": "Українська",
        "EN": "English", 
        "DE": "Deutsch",
        "FR": "Français",
        "ES": "Español",
        "PL": "Polski"
    }
    return languages.get(lang_code, lang_code)

async def choose_source_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ОРИГІНАЛУ - з фільтром та станом"""
    try:
        logger.info(f"ВИБІР МОВИ ОРИГІНАЛУ: {callback.data} для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data:
            await callback.answer("⚠️ Помилка даних")
            return
            
        if not callback.data.startswith("lang_"):
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        
        # Отримуємо мову
        language_code = callback.data.split("_")[1]
        await state.update_data(source_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_target_language
        
        # Відображаємо вибрану мову
        selected_lang = _get_language_name(language_code)
        await callback.message.answer(f"✅ Вибрано мову оригіналу: {selected_lang}")
        
        # Відправляємо вибір мови перекладу
        await callback.message.answer("<b>Крок 3/5:</b> Оберіть мову перекладу:", parse_mode="HTML")
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_UK"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_EN")
        )
        keyboard.add(
            types.InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_DE"),
            types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_FR")
        )
        keyboard.add(
            types.InlineKeyboardButton("🇪🇸 Español", callback_data="lang_ES"),
            types.InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_PL")
        )
        
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        logger.info(f"МОВА ОРИГІНАЛУ {language_code} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_source_language: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ПЕРЕКЛАДУ - з фільтром та станом"""
    try:
        logger.info(f"ВИБІР МОВИ ПЕРЕКЛАДУ: {callback.data} для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data:
            await callback.answer("⚠️ Помилка даних")
            return
            
        if not callback.data.startswith("lang_"):
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
            return
        
        await state.update_data(target_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_file
        
        # Відображаємо вибрану мову
        selected_lang = _get_language_name(language_code)
        await callback.message.answer(f"✅ Вибрано мову перекладу: {selected_lang}")
        
        # Відправляємо запит на файл
        await callback.message.answer("<b>Крок 4/5:</b> Надішліть файл для перекладу (txt, docx, pdf)", parse_mode="HTML")
        
        logger.info(f"МОВА ПЕРЕКЛАДУ {language_code} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_target_language: {str(e)}")
        await callback.answer("⚠️ Помилка")

def register_handlers_language(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ МОВ - правильний порядок"""
    # Вибір мови оригіналу - з фільтром та станом
    dp.register_callback_query_handler(
        choose_source_language, 
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_source_language
    )
    
    # Вибір мови перекладу - з фільтром та станом
    dp.register_callback_query_handler(
        choose_target_language, 
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_target_language
    )