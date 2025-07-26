from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_language_keyboard
from states import TranslationStates
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def choose_source_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ОРИГІНАЛУ"""
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
        
        # Відправляємо вибір мови перекладу
        await callback.message.answer("🌍 Оберіть мову перекладу:")
        keyboard = get_language_keyboard()
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        log_user_action(callback.from_user.id, "selected_source_language", language_code)
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_source_language: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ПЕРЕКЛАДУ"""
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
        await state.update_data(target_language=language_code)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_file
        
        # Відправляємо запит на файл
        await callback.message.answer("📥 Надішліть файл для перекладу (txt, docx, pdf)")
        
        log_user_action(callback.from_user.id, "selected_target_language", language_code)
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_target_language: {str(e)}")
        await callback.answer("⚠️ Помилка")

def register_handlers_language(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ МОВ"""
    # Вибір мови оригіналу - БЕЗ ОБМЕЖЕНЬ
    dp.register_callback_query_handler(choose_source_language)
    
    # Вибір мови перекладу - БЕЗ ОБМЕЖЕНЬ
    dp.register_callback_query_handler(choose_target_language)