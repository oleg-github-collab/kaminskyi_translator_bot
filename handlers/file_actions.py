from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """Обробка кнопки оплати"""
    try:
        await callback.answer()
        
        # Переходимо до стану оплати
        await TranslationStates.next()  # waiting_for_payment_confirmation -> translating
        
        await callback.message.answer("🔄 Переходимо до оплати...")
        await callback.message.answer("⚠️ Увага: Система оплати тимчасово в розробці. Натисніть /translate для тестового перекладу")
        
        log_user_action(callback.from_user.id, "clicked_payment_button")
        
    except Exception as e:
        logger.error(f"Error in process_payment for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка", show_alert=True)

async def upload_another(callback: types.CallbackQuery, state: FSMContext):
    """Обробка кнопки завантаження іншого файлу"""
    try:
        await callback.answer()
        
        # Повертаємося до стану очікування файлу
        await TranslationStates.waiting_for_file.set()
        
        # Видаляємо попередній файл якщо він є
        user_data = await state.get_data()
        file_path = user_data.get('file_path')
        if file_path:
            import os
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        
        await callback.message.answer("📥 Надішліть інший файл для перекладу (txt, docx, pdf):")
        
        log_user_action(callback.from_user.id, "clicked_upload_another")
        
    except Exception as e:
        logger.error(f"Error in upload_another for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка", show_alert=True)

def register_handlers_file_actions(dp):
    dp.register_callback_query_handler(process_payment, lambda c: c.data == "process_payment")
    dp.register_callback_query_handler(upload_another, lambda c: c.data == "upload_another")
