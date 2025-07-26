from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_language_keyboard
from states import TranslationStates
from locales.messages import MESSAGES
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def choose_source_language(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        language_code = callback.data.split("_")[1]  # lang_EN, lang_DE тощо
        await state.update_data(source_language=language_code)
        await TranslationStates.next()  # Переходимо до waiting_for_target_language
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        message_text = MESSAGES["choose_target_language"][user_lang]
        keyboard = get_language_keyboard()
        await callback.message.edit_text(message_text, reply_markup=keyboard)
        log_user_action(callback.from_user.id, "selected_source_language", language_code)
    except Exception as e:
        logger.error(f"Error in choose_source_language for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору мови.")

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        language_code = callback.data.split("_")[1]  # lang_EN, lang_DE тощо
        await state.update_data(target_language=language_code)
        await TranslationStates.next()  # Переходимо до waiting_for_file
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        message_text = MESSAGES["send_file"][user_lang]
        await callback.message.edit_text(message_text)
        log_user_action(callback.from_user.id, "selected_target_language", language_code)
    except Exception as e:
        logger.error(f"Error in choose_target_language for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору мови.")

def register_handlers_language(dp):
    # Для вибору мови оригіналу
    dp.register_callback_query_handler(choose_source_language, 
                                    lambda c: c.data.startswith("lang_"), 
                                    state=TranslationStates.waiting_for_source_language)
    # Для вибору мови перекладу
    dp.register_callback_query_handler(choose_target_language, 
                                    lambda c: c.data.startswith("lang_"), 
                                    state=TranslationStates.waiting_for_target_language)