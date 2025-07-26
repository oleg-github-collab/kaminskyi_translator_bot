from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_language_keyboard
from states import TranslationStates
from locales.messages import MESSAGES
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def choose_source_language(callback: types.CallbackQuery, state: FSMContext):
    """Обробка вибору мови оригіналу"""
    try:
        await callback.answer()
        
        # Отримуємо вибрану мову
        language_code = callback.data.split("_")[1]  # lang_EN, lang_DE тощо
        
        # Зберігаємо мову оригіналу в стані
        await state.update_data(source_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_target_language
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Відправляємо повідомлення з вибором мови перекладу
        message_text = "🎯 <b>Крок 3 з 5:</b> " + MESSAGES["choose_target_language"][user_lang]
        keyboard = get_language_keyboard()
        await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "selected_source_language", language_code)
        
    except Exception as e:
        logger.error(f"Error in choose_source_language for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору мови", show_alert=True)

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    """Обробка вибору мови перекладу"""
    try:
        await callback.answer()
        
        # Отримуємо вибрану мову
        language_code = callback.data.split("_")[1]  # lang_EN, lang_DE тощо
        
        # Зберігаємо мову перекладу в стані
        await state.update_data(target_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_file
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Відправляємо повідомлення про надсилання файлу
        message_text = "🎯 <b>Крок 4 з 5:</b> " + MESSAGES["send_file"][user_lang]
        await callback.message.answer(message_text, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "selected_target_language", language_code)
        
    except Exception as e:
        logger.error(f"Error in choose_target_language for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору мови", show_alert=True)

def register_handlers_language(dp):
    """Реєстрація handler'ів для вибору мов"""
    # Для вибору мови оригіналу
    dp.register_callback_query_handler(choose_source_language, 
                                     lambda c: c.data and c.data.startswith("lang_"), 
                                     state=TranslationStates.waiting_for_source_language)
    
    # Для вибору мови перекладу
    dp.register_callback_query_handler(choose_target_language, 
                                     lambda c: c.data and c.data.startswith("lang_"), 
                                     state=TranslationStates.waiting_for_target_language)