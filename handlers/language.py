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
        model = callback.data.split("_")[1]
        await state.update_data(model=model)
        await TranslationStates.next()
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        await callback.message.edit_text(MESSAGES["choose_source_language"][user_lang], 
                                       reply_markup=get_language_keyboard())
        log_user_action(callback.from_user.id, "selected_model", model)
    except Exception as e:
        logger.error(f"Error in choose_source_language for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору моделі.")

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        language_code = callback.data.split("_")[1]
        await state.update_data(source_language=language_code)
        await TranslationStates.next()
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        await callback.message.edit_text(MESSAGES["choose_target_language"][user_lang], 
                                       reply_markup=get_language_keyboard())
        log_user_action(callback.from_user.id, "selected_source_language", language_code)
    except Exception as e:
        logger.error(f"Error in choose_target_language for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору мови.")

def register_handlers_language(dp):
    dp.register_callback_query_handler(choose_source_language, 
                                    lambda c: c.data.startswith("model_"), 
                                    state=TranslationStates.choosing_model)
    dp.register_callback_query_handler(choose_target_language, 
                                    lambda c: c.data.startswith("lang_"), 
                                    state=TranslationStates.waiting_for_source_language)