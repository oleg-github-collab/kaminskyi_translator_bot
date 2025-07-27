from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging

logger = logging.getLogger(__name__)

async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ОПЛАТИ"""
    try:
        logger.info(f"💳 ОБРОБКА ОПЛАТИ для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Переходимо до стану оплати
        await TranslationStates.waiting_for_payment_confirmation.set()
        
        # Заглушка для оплати
        await callback.message.answer("💳 <b>Крок 5/5:</b> Оплата", parse_mode="HTML")
        await callback.message.answer("⚠️ Система оплати в розробці. Натисніть кнопку нижче для продовження.")
        
        # Кнопка продовження без оплати (для тестування)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("⏭ Продовжити без оплати", callback_data="payment_done"))
        keyboard.add(types.InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
        
        await callback.message.answer("Виберіть дію:", reply_markup=keyboard)
        
        logger.info(f"✅ ОПЛАТА ініційована для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в process_payment для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def payment_done(callback: types.CallbackQuery, state: FSMContext):
    """ОПЛАТА ЗДІЙСНЕНА"""
    try:
        logger.info(f"✅ ОПЛАТА ПІДТВЕРДЖЕНА для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Переходимо до перекладу
        await TranslationStates.translating.set()
        
        await callback.message.answer("✅ Оплата підтверджена!")
        await callback.message.answer("🔄 Починаємо переклад файлу...")
        
        logger.info(f"✅ ОПЛАТА підтверджена для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в payment_done для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def upload_another(callback: types.CallbackQuery, state: FSMContext):
    """ЗАВАНТАЖИТИ ІНШИЙ ФАЙЛ"""
    try:
        logger.info(f"🔄 ІНШИЙ ФАЙЛ для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Повертаємося до стану очікування файлу
        await TranslationStates.waiting_for_file.set()
        
        await callback.message.answer("📥 Надішліть інший файл для перекладу (txt, docx, pdf)")
        logger.info(f"✅ ІНШИЙ ФАЙЛ ініційовано для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в upload_another для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

def register_handlers_payment(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ ОПЛАТИ"""
    dp.register_callback_query_handler(
        process_payment,
        lambda c: c.data == "process_payment",
        state=TranslationStates.waiting_for_payment_confirmation,
    )
    dp.register_callback_query_handler(
        payment_done,
        lambda c: c.data == "payment_done",
        state=TranslationStates.waiting_for_payment_confirmation,
    )
    dp.register_callback_query_handler(
        upload_another,
        lambda c: c.data == "upload_another",
        state=TranslationStates.waiting_for_payment_confirmation,
    )