from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from keyboards.inline import get_continue_keyboard
from utils.payment_utils import check_payment_status
import logging

logger = logging.getLogger(__name__)

async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """Обробка кнопки оплати"""
    try:
        logger.info(f"=== ПРОЦЕС ОПЛАТИ === User: {callback.from_user.id}")
        await callback.answer()
        
        user_data = await state.get_data()
        price = user_data.get('price', 0)
        
        await callback.message.answer(
            f"💳 <b>Оплата {price} €</b>\n\n"
            "Перейдіть за посиланням для оплати.\n"
            "Після успішної оплати переклад почнеться автоматично.",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Помилка в process_payment: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка оплати")

async def payment_done(callback: types.CallbackQuery, state: FSMContext):
    """Підтвердження оплати"""
    try:
        logger.info(f"=== ПІДТВЕРДЖЕННЯ ОПЛАТИ === User: {callback.from_user.id}")
        await callback.answer()
        
        # Перевірка статусу оплати
        user_data = await state.get_data()
        
        # TODO: Тут має бути реальна перевірка оплати
        payment_confirmed = True  # Заглушка
        
        if payment_confirmed:
            await TranslationStates.translating.set()
            await callback.message.answer("✅ <b>Оплата підтверджена!</b>\n\n⏳ Починаю переклад...", parse_mode="HTML")
            
            # TODO: Тут має бути виклик функції перекладу
            # translation_result = await translate_file(user_data)
            
            # Імітація перекладу
            await callback.message.answer("📄 <b>Переклад завершено!</b>\n\nФайл готовий до завантаження.", parse_mode="HTML")
            
            await TranslationStates.completed.set()
            
            # Кнопки для продовження
            keyboard = get_continue_keyboard()
            await callback.message.answer("Що далі?", reply_markup=keyboard)
        else:
            await callback.message.answer("⚠️ Оплата не підтверджена. Спробуйте ще раз.", parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Помилка в payment_done: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка")

def register_handlers_payment(dp):
    """Реєстрація обробників оплати"""
    logger.info("=== РЕЄСТРАЦІЯ ОБРОБНИКІВ ОПЛАТИ ===")
    
    # Обробка кнопки оплати
    dp.register_callback_query_handler(
        process_payment,
        lambda c: c.data and c.data == "process_payment",
        state=TranslationStates.waiting_for_payment_confirmation
    )
    
    # Підтвердження оплати
    dp.register_callback_query_handler(
        payment_done,
        lambda c: c.data and c.data == "payment_done",
        state=TranslationStates.waiting_for_payment_confirmation
    )
    
    logger.info("=== ОБРОБНИКИ ОПЛАТИ ЗАРЕЄСТРОВАНО ===")