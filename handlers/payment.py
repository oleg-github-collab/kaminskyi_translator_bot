from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from utils.logger import log_user_action, log_error
import logging

logger = logging.getLogger(__name__)

async def payment_done(callback: types.CallbackQuery, state: FSMContext):
    """Обробка підтвердження оплати"""
    try:
        await callback.answer()
        
        # Переходимо до перекладу
        await TranslationStates.translating.set()
        
        await callback.message.answer("✅ Оплата підтверджена! Починаємо переклад...")
        await callback.message.answer("🔄 Перекладаємо файл...")
        
        log_user_action(callback.from_user.id, "payment_confirmed")
        
    except Exception as e:
        logger.error(f"Error in payment_done for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка", show_alert=True)

async def upload_another_file(callback: types.CallbackQuery, state: FSMContext):
    """Обробка кнопки завантаження іншого файлу"""
    try:
        await callback.answer()
        
        # Повертаємося до стану очікування файлу
        await TranslationStates.waiting_for_file.set()
        
        # Очищуємо попередні дані
        user_data = await state.get_data()
        file_path = user_data.get('file_path')
        if file_path:
            import os
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        
        await state.update_data(
            file_path=None,
            file_extension=None,
            char_count=None,
            price=None
        )
        
        await callback.message.answer("📥 Надішліть інший файл для перекладу (txt, docx, pdf):")
        
        log_user_action(callback.from_user.id, "upload_another_file")
        
    except Exception as e:
        logger.error(f"Error in upload_another_file for user {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка", show_alert=True)

def register_handlers_payment(dp):
    dp.register_callback_query_handler(payment_done, lambda c: c.data == "payment_done")
    dp.register_callback_query_handler(upload_another_file, lambda c: c.data == "upload_another")