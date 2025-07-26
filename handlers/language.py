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
        logger.info(f"Вибір мови оригіналу для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data or not callback.data.startswith("lang_"):
            await callback.answer("⚠️ Невірні дані", show_alert=True)
            return
            
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
        message_text = "🎯 <b>Крок 3/5:</b> Мова перекладу"
        keyboard = get_language_keyboard()
        await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "selected_source_language", language_code)
        logger.info(f"Мова оригіналу {language_code} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_source_language для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка вибору мови", show_alert=True)

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    """Обробка вибору мови перекладу"""
    try:
        logger.info(f"Вибір мови перекладу для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data or not callback.data.startswith("lang_"):
            await callback.answer("⚠️ Невірні дані", show_alert=True)
            return
            
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
        message_text = "🎯 <b>Крок 4/5:</b> Надішліть файл\n📄 Підтримуються: TXT, DOCX, PDF"
        await callback.message.answer(message_text, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "selected_target_language", language_code)
        logger.info(f"Мова перекладу {language_code} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_target_language для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
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