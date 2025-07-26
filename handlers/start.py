from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_model_keyboard, get_continue_keyboard
from states import TranslationStates
from locales.messages import MESSAGES
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """Обробка команди /start - завжди починаємо з чистого стану"""
    # Завжди скидаємо стан
    await state.finish()
    user_lang = message.from_user.language_code or "en"
    user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
    
    try:
        welcome_message = MESSAGES["start"][user_lang]
        await message.answer(welcome_message, parse_mode="HTML")
        await TranslationStates.choosing_model.set()
        keyboard = get_model_keyboard(user_lang)
        await message.answer("🎯 <b>Крок 1 з 5:</b> Оберіть модель перекладу", 
                           reply_markup=keyboard, parse_mode="HTML")
        log_user_action(message.from_user.id, "started_bot", f"language: {user_lang}")
    except Exception as e:
        logger.error(f"Error in cmd_start for user {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ <b>Помилка запуску</b>\nСпробуйте ще раз команду /start", 
                           parse_mode="HTML")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    """Обробка вибору моделі перекладу"""
    try:
        await callback.answer()
        model = callback.data.split("_")[1]  # model_basic або model_epic
        await state.update_data(model=model)
        await TranslationStates.next()  # Переходимо до waiting_for_source_language
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        message_text = "🎯 <b>Крок 2 з 5:</b> " + MESSAGES["choose_source_language"][user_lang]
        keyboard = get_language_keyboard()
        await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.message.delete()  # Видаляємо попереднє повідомлення
        log_user_action(callback.from_user.id, "selected_model", model)
    except Exception as e:
        logger.error(f"Error in choose_model for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору моделі", show_alert=True)

async def continue_translate(callback: types.CallbackQuery, state: FSMContext):
    """Обробка продовження перекладу"""
    try:
        await callback.answer()
        # Завжди починаємо з чистого стану
        await state.finish()
        await TranslationStates.choosing_model.set()
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        welcome_message = MESSAGES["start"][user_lang]
        await callback.message.answer(welcome_message, parse_mode="HTML")
        keyboard = get_model_keyboard(user_lang)
        await callback.message.answer("🎯 <b>Крок 1 з 5:</b> Оберіть модель перекладу", 
                                    reply_markup=keyboard, parse_mode="HTML")
        await callback.message.delete()  # Видаляємо попереднє повідомлення
        log_user_action(callback.from_user.id, "continued_translation")
    except Exception as e:
        logger.error(f"Error in continue_translate for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка", show_alert=True)

async def exit_bot(callback: types.CallbackQuery, state: FSMContext):
    """Обробка виходу з бота"""
    try:
        await callback.answer()
        await state.finish()
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        exit_message = "👋 " + MESSAGES["thank_you"][user_lang].split('\n')[0]
        await callback.message.answer(exit_message, parse_mode="HTML")
        await callback.message.delete()  # Видаляємо попереднє повідомлення
        log_user_action(callback.from_user.id, "exited_bot")
    except Exception as e:
        logger.error(f"Error in exit_bot for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка", show_alert=True)

def register_handlers_start(dp):
    # Обробка команди /start в будь-якому стані
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    # Обробка вибору моделі
    dp.register_callback_query_handler(choose_model, lambda c: c.data.startswith("model_"), 
                                     state=TranslationStates.choosing_model)
    # Обробка продовження перекладу
    dp.register_callback_query_handler(continue_translate, lambda c: c.data == "continue_translate")
    # Обробка виходу
    dp.register_callback_query_handler(exit_bot, lambda c: c.data == "exit")