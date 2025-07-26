from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_model_keyboard, get_continue_keyboard
from states import TranslationStates
from locales.messages import MESSAGES
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    user_lang = message.from_user.language_code or "en"
    user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
    
    try:
        await message.answer(MESSAGES["start"][user_lang], parse_mode="HTML")
        await TranslationStates.choosing_model.set()
        await message.answer("Оберіть модель:", reply_markup=get_model_keyboard(user_lang))
        log_user_action(message.from_user.id, "started_bot", f"language: {user_lang}")
    except Exception as e:
        logger.error(f"Error in cmd_start for user {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ Виникла помилка. Спробуйте ще раз.")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        model = callback.data.split("_")[1]
        await state.update_data(model=model)
        await TranslationStates.next()
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        await callback.message.edit_text(MESSAGES["choose_source_language"][user_lang])
        log_user_action(callback.from_user.id, "selected_model", model)
    except Exception as e:
        logger.error(f"Error in choose_model for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору моделі.")

async def continue_translate(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        await TranslationStates.choosing_model.set()
        await callback.message.edit_text(MESSAGES["start"][user_lang], parse_mode="HTML")
        await callback.message.answer("Оберіть модель:", reply_markup=get_model_keyboard(user_lang))
        log_user_action(callback.from_user.id, "continued_translation")
    except Exception as e:
        logger.error(f"Error in continue_translate for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка.")

async def exit_bot(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await state.finish()
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        await callback.message.edit_text("👋 " + MESSAGES["thank_you"][user_lang].split('\n')[0])
        log_user_action(callback.from_user.id, "exited_bot")
    except Exception as e:
        logger.error(f"Error in exit_bot for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка.")

def register_handlers_start(dp):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_callback_query_handler(choose_model, lambda c: c.data.startswith("model_"), 
                                     state=TranslationStates.choosing_model)
    dp.register_callback_query_handler(continue_translate, lambda c: c.data == "continue_translate")
    dp.register_callback_query_handler(exit_bot, lambda c: c.data == "exit")