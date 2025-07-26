from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.payment_utils import create_payment_session
from states import TranslationStates
from keyboards.inline import get_payment_keyboard
from locales.messages import MESSAGES
from utils.logger import log_user_action, log_error
import logging

logger = logging.getLogger(__name__)

async def process_payment(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        price = user_data.get('price')
        char_count = user_data.get('char_count')
        model = user_data.get('model')
        user_id = message.from_user.id
        
        if not price or not char_count or not model:
            await message.answer("⚠️ Помилка даних. Спробуйте ще раз.")
            return
        
        payment_url = create_payment_session(price, user_id, char_count, model)
        
        if not payment_url:
            await message.answer("⚠️ Помилка створення платежу. Спробуйте пізніше.")
            return
        
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        keyboard = get_payment_keyboard(payment_url, user_lang)
        
        model_name = config.MODELS[model]["name"]
        payment_message = MESSAGES["file_stats"][user_lang].format(
            chars=char_count,
            model=model_name,
            price=price
        )
        
        await message.answer(f"💳 {payment_message}", reply_markup=keyboard)
        log_user_action(user_id, "payment_initiated", 
                       f"amount: {price}€, chars: {char_count}, model: {model}")
        
    except Exception as e:
        log_error(e, f"Payment processing for user {message.from_user.id}")
        await message.answer("⚠️ Помилка обробки платежу. Спробуйте ще раз.")

async def check_payment(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer("✅ Оплата підтверджена! Починаємо переклад...")
        await TranslationStates.next()
        
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        model_name = config.MODELS[model]["name"]
        
        await callback.message.edit_text(
            MESSAGES["translation_progress"][user_lang].format(model=model_name, progress=0)
        )
        log_user_action(callback.from_user.id, "payment_confirmed")
        
    except Exception as e:
        log_error(e, f"Payment check for user {callback.from_user.id}")
        await callback.answer("⚠️ Помилка перевірки оплати.")

def register_handlers_payment(dp):
    dp.register_message_handler(process_payment, state=TranslationStates.waiting_for_payment_confirmation)
    dp.register_callback_query_handler(check_payment, lambda c: c.data == "check_payment")