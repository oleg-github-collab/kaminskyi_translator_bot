from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from utils.simple_debug import debug_callback, log_action
from utils.file_validation import get_supported_formats_text
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
        
        log_action("clicked_payment_button", callback.from_user.id, "user clicked payment")
        
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
        
        await callback.message.answer(
            "📥 **Надішліть інший файл для перекладу:**\n\n" + get_supported_formats_text(),
            parse_mode="Markdown"
        )
        
        log_action("clicked_upload_another", callback.from_user.id, "user wants to upload another file")
        
    except Exception as e:
        logger.error(f"Error in upload_another for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка", show_alert=True)

def register_handlers_file_actions(dp):
    dp.register_callback_query_handler(process_payment, lambda c: c.data == "process_payment")
    dp.register_callback_query_handler(upload_another, lambda c: c.data == "upload_another")