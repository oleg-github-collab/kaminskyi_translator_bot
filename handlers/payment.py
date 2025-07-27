from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging
from utils.payment_utils import create_payment_session
from utils.payment_utils import create_payment_session, verify_payment
from handlers.translate import start_translation

logger = logging.getLogger(__name__)

async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ОПЛАТИ"""
    try:
        logger.info(f"💳 ОБРОБКА ОПЛАТИ для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Дані для оплати
        user_data = await state.get_data()
        price = user_data.get("price", 0.0)
        char_count = user_data.get("char_count", 0)
        model = user_data.get("model", "basic")

        session_url, session_id = create_payment_session(
            price, callback.from_user.id, char_count, model
        ) or (None, None)

        if not session_url:
            await callback.message.answer("⚠️ Не вдалося створити сесію оплати")
            return

        await state.update_data(payment_session=session_id)

        await callback.message.answer(
            "💳 <b>Крок 5/5:</b> Оплата",
            parse_mode="HTML",
        )

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                "💳 Перейти до оплати", url=session_url
            )
        )
        keyboard.add(
            types.InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another")
        )

        await callback.message.answer("Натисніть кнопку, щоб оплатити", reply_markup=keyboard)
        
        logger.info(f"✅ ОПЛАТА ініційована для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в process_payment для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def payment_done(callback: types.CallbackQuery, state: FSMContext):
    """ОПЛАТА ЗДІЙСНЕНА"""
    try:
        await callback.answer()

        data = await state.get_data()
        session_id = data.get("payment_session")

        if not session_id:
            await callback.message.answer("⚠️ Сесію оплати не знайдено")
            return

        result = verify_payment(session_id)
        if not result.get("paid"):
            await callback.message.answer("⚠️ Оплата ще не підтверджена")
            return

        await TranslationStates.translating.set()

        await callback.message.answer("✅ Оплата підтверджена!")
        await callback.message.answer("🔄 Починаємо переклад файлу...")

        logger.info(
            f"✅ ОПЛАТА підтверджена для користувача {callback.from_user.id}"
        )

        # Запускаємо переклад автоматично
        await start_translation(callback.message, state)

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
        upload_another,
        lambda c: c.data == "upload_another",
        state=TranslationStates.waiting_for_payment_confirmation,
    )
