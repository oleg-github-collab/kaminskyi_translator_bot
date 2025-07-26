from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from utils.logger import log_user_action, log_error
from keyboards.inline import get_payment_action_keyboard, get_continue_keyboard
import logging

logger = logging.getLogger(__name__)

async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """Обробка кнопки оплати"""
    try:
        logger.info(f"Натиснута кнопка оплати для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Переходимо до стану оплати
        await TranslationStates.next()  # translating
        
        await callback.message.answer("🔄 Переходимо до оплати...")
        await callback.message.answer("⚠️ Увага: Система оплати тимчасово в розробці. Натисніть кнопку нижче для продовження")
        
        # Клавіатура для продовження
        keyboard = get_payment_action_keyboard()
        await callback.message.answer("Виберіть дію:", reply_markup=keyboard)
        
        log_user_action(callback.from_user.id, "clicked_payment_button")
        logger.info(f"Кнопка оплати оброблена для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в process_payment для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка", show_alert=True)

async def payment_done(callback: types.CallbackQuery, state: FSMContext):
    """Обробка підтвердження оплати"""
    try:
        logger.info(f"Оплата підтверджена для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Переходимо до перекладу
        await TranslationStates.translating.set()
        
        await callback.message.answer("✅ Оплата підтверджена!")
        await callback.message.answer("🔄 Починаємо переклад файлу...")
        
        log_user_action(callback.from_user.id, "payment_confirmed")
        logger.info(f"Оплата підтверджена для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в payment_done для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка", show_alert=True)

async def upload_another_file(callback: types.CallbackQuery, state: FSMContext):
    """Обробка кнопки завантаження іншого файлу"""
    try:
        logger.info(f"Натиснута кнопка 'інший файл' для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Повертаємося до стану очікування файлу
        await TranslationStates.waiting_for_file.set()
        
        # Очищуємо попередні дані файлу
        user_data = await state.get_data()
        file_path = user_data.get('file_path')
        if file_path:
            import os
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Попередній файл видалено: {file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Помилка видалення файлу {file_path}: {str(cleanup_error)}")
        
        # Оновлюємо дані стану
        await state.update_data(
            file_path=None,
            file_extension=None,
            char_count=None,
            price=None
        )
        
        await callback.message.answer("📥 Надішліть інший файл для перекладу (txt, docx, pdf):")
        
        log_user_action(callback.from_user.id, "upload_another_file")
        logger.info(f"Перехід до іншого файлу для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в upload_another_file для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка", show_alert=True)

def register_handlers_payment(dp):
    dp.register_callback_query_handler(process_payment, lambda c: c.data == "process_payment")
    dp.register_callback_query_handler(payment_done, lambda c: c.data == "payment_done")
    dp.register_callback_query_handler(upload_another_file, lambda c: c.data == "upload_another")