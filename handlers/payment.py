from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from utils.payment_utils import create_payment_session, calculate_price
from utils.error_handler import payment_error_handler, log_payment_action, validate_payment_data, safe_state_update
from keyboards.inline import get_payment_action_keyboard
import config
import logging

logger = logging.getLogger(__name__)

@payment_error_handler
async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ОПЛАТИ"""
    try:
        logger.info(f"💳 ОБРОБКА ОПЛАТИ для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Отримуємо дані з state
        data = await state.get_data()
        char_count = data.get('char_count', 0)
        model = data.get('model', 'basic')
        user_id = callback.from_user.id
        
        # Валідація даних
        payment_data = {
            'char_count': char_count,
            'model': model,
            'amount': calculate_price(char_count, model)
        }
        
        if not validate_payment_data(payment_data):
            await callback.message.answer(
                "❌ <b>Помилка валідації даних</b>\n\n"
                "Будь ласка, завантажте файл заново.",
                parse_mode="HTML"
            )
            log_payment_action("validation_failed", user_id, payment_data)
            return
        
        # Розраховуємо ціну
        price_eur = calculate_price(char_count, model)
        model_name = config.MODELS[model]['name']
        
        # Логуємо початок процесу оплати
        log_payment_action("payment_initiated", user_id, {
            'char_count': char_count,
            'model': model,
            'amount': price_eur
        })
        
        await callback.message.answer("💳 <b>Крок 5/5:</b> Оплата", parse_mode="HTML")
        
        # Створюємо Stripe сесію
        payment_url = create_payment_session(price_eur, user_id, char_count, model)
        
        if payment_url:
            # Переходимо до стану оплати
            await TranslationStates.waiting_for_payment_confirmation.set()
            await safe_state_update(state, payment_url=payment_url, amount=price_eur, payment_initiated=True)
            
            # Повідомлення з деталями оплати
            payment_details = (
                f"📊 <b>Деталі оплати:</b>\n"
                f"📝 Символів: {char_count:,}\n"
                f"🎯 Модель: {model_name}\n"
                f"💰 Сума: {price_eur}€\n\n"
                f"🔒 Безпечна оплата через Stripe\n"
                f"💳 Приймаємо всі банківські карти"
            )
            await callback.message.answer(payment_details, parse_mode="HTML")
            
            # Кнопка оплати з URL
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("💳 Сплатити зараз", url=payment_url))
            keyboard.add(types.InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
            keyboard.add(types.InlineKeyboardButton("❓ Підтримка", callback_data="payment_help"))
            
            await callback.message.answer(
                "🚀 <b>Натисніть кнопку нижче для оплати:</b>\n\n"
                "⚡ Оплата відкриється в безпечному вікні Stripe\n"
                "🔄 Після успішної оплати поверніться до бота",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
            logger.info(f"✅ STRIPE СЕСІЯ створена для користувача {user_id}, сума: {price_eur}€")
        else:
            await callback.message.answer(
                "❌ <b>Помилка створення платежу</b>\n\n"
                "Спробуйте пізніше або зверніться до підтримки",
                parse_mode="HTML"
            )
            logger.error(f"❌ Не вдалося створити Stripe сесію для користувача {user_id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в process_payment для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка при створенні платежу")
        await callback.message.answer(
            "❌ <b>Технічна помилка</b>\n\n"
            "Спробуйте ще раз або зверніться до підтримки",
            parse_mode="HTML"
        )

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

async def payment_help(callback: types.CallbackQuery, state: FSMContext):
    """ДОВІДКА ПО ОПЛАТІ"""
    try:
        await callback.answer()
        help_text = (
            "❓ <b>Довідка по оплаті:</b>\n\n"
            "🔒 <b>Безпека:</b> Всі платежі обробляються через Stripe - найнадійнішу платіжну систему\n\n"
            "💳 <b>Способи оплати:</b>\n"
            "• Visa, Mastercard, American Express\n"
            "• Google Pay, Apple Pay\n"
            "• Банківські переказі\n\n"
            "⚡ <b>Швидкість:</b> Платіж обробляється миттєво\n\n"
            "🔄 <b>Повернення:</b> Якщо виникли проблеми, зверніться до підтримки\n\n"
            "📧 <b>Підтримка:</b> @KaminskyiSupport"
        )
        await callback.message.answer(help_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в payment_help: {str(e)}")

async def start_translation(callback: types.CallbackQuery, state: FSMContext):
    """ПОЧАТОК ПЕРЕКЛАДУ ПІСЛЯ ОПЛАТИ"""
    try:
        logger.info(f"🚀 ПОЧАТОК ПЕРЕКЛАДУ для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Переходимо до стану перекладу
        await TranslationStates.translating.set()
        
        await callback.message.answer("✅ Оплата підтверджена!")
        await callback.message.answer("🔄 Починаємо переклад файлу...")
        
        logger.info(f"✅ ПЕРЕКЛАД розпочато для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в start_translation для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка при початку перекладу")

async def payment_details(callback: types.CallbackQuery, state: FSMContext):
    """ДЕТАЛЬНА ІНФОРМАЦІЯ ПРО ОПЛАТУ"""
    try:
        await callback.answer()
        data = await state.get_data()
        char_count = data.get('char_count', 0)
        model = data.get('model', 'basic')
        
        price_eur = calculate_price(char_count, model)
        model_info = config.MODELS[model]
        
        details_text = (
            f"💰 <b>Детальна інформація про оплату:</b>\n\n"
            f"🎯 <b>Модель:</b> {model_info['name']}\n"
            f"📝 <b>Опис:</b> {model_info['description']}\n"
            f"📊 <b>Символів до перекладу:</b> {char_count:,}\n"
            f"💵 <b>Ціна за одиницю:</b> {model_info['price_per_unit']:.2f}€ за {config.CHARS_PER_UNIT} символів\n"
            f"💰 <b>Мінімальна ціна:</b> {model_info['min_price']:.2f}€\n"
            f"🧮 <b>Розрахунок:</b> {char_count} ÷ {config.CHARS_PER_UNIT} × {model_info['price_per_unit']:.2f}€\n"
            f"💳 <b>До сплати:</b> {price_eur:.2f}€\n\n"
            f"🔒 <b>Безпека:</b> Платіж через Stripe (SSL шифрування)\n"
            f"⚡ <b>Швидкість:</b> Миттєва обробка платежу"
        )
        
        await callback.message.answer(details_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в payment_details: {str(e)}")
        await callback.answer("⚠️ Помилка отримання деталей")

async def contact_support(callback: types.CallbackQuery, state: FSMContext):
    """КОНТАКТ З ПІДТРИМКОЮ"""
    try:
        await callback.answer()
        support_text = (
            f"🆘 <b>Служба підтримки</b>\n\n"
            f"📧 <b>Email:</b> support@kaminskyi.ai\n"
            f"💬 <b>Telegram:</b> @KaminskyiSupport\n"
            f"🕐 <b>Години роботи:</b> 9:00 - 21:00 (UTC+2)\n\n"
            f"📝 <b>Перед зверненням підготуйте:</b>\n"
            f"• ID користувача: {callback.from_user.id}\n"
            f"• Опис проблеми\n"
            f"• Скріншоти (за потреби)\n\n"
            f"⚡ <b>Середній час відповіді:</b> до 2 годин"
        )
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💬 Написати в Telegram", url="https://t.me/KaminskyiSupport"))
        keyboard.add(types.InlineKeyboardButton("📧 Написати Email", url="mailto:support@kaminskyi.ai"))
        keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_payment"))
        
        await callback.message.answer(support_text, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в contact_support: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def view_receipt(callback: types.CallbackQuery, state: FSMContext):
    """ПЕРЕГЛЯД ЧЕКУ"""
    try:
        await callback.answer()
        data = await state.get_data()
        
        if not data.get('payment_completed'):
            await callback.message.answer("❌ Чек недоступний - оплата не завершена")
            return
            
        from utils.payment_utils import format_payment_receipt
        receipt_text = format_payment_receipt(data)
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📧 Надіслати на email", callback_data="email_receipt"))
        keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
        
        await callback.message.answer(receipt_text, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в view_receipt: {str(e)}")
        await callback.answer("⚠️ Помилка отримання чеку")

def register_handlers_payment(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ ОПЛАТИ"""
    dp.register_callback_query_handler(process_payment, lambda c: c.data and c.data == "process_payment")
    dp.register_callback_query_handler(payment_done, lambda c: c.data and c.data == "payment_done")
    dp.register_callback_query_handler(upload_another, lambda c: c.data and c.data == "upload_another")
    dp.register_callback_query_handler(payment_help, lambda c: c.data and c.data == "payment_help")
    dp.register_callback_query_handler(start_translation, lambda c: c.data and c.data == "start_translation")
    dp.register_callback_query_handler(payment_details, lambda c: c.data and c.data == "payment_details")
    dp.register_callback_query_handler(contact_support, lambda c: c.data and c.data == "contact_support")
    dp.register_callback_query_handler(view_receipt, lambda c: c.data and c.data == "view_receipt")