import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.file_utils import count_chars_in_file
from utils.payment_utils import calculate_price, create_payment_session
from states import TranslationStates
from locales.messages import MESSAGES
from config import TEMP_DIR
from utils.logger import log_user_action, log_error
import logging

logger = logging.getLogger(__name__)

async def handle_file(message: types.Message, state: FSMContext):
    """Обробка файлу з реальною кнопкою оплати"""
    try:
        logger.info(f"File handler started for user {message.from_user.id}")
        
        # Перевірка наявності файлу
        if not message.document:
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file"][user_lang], parse_mode="HTML")
            return
        
        # Перевірка типу файлу
        file_extension = os.path.splitext(message.document.file_name)[1].lower()
        if file_extension not in ['.txt', '.docx', '.pdf']:
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file_type"][user_lang], parse_mode="HTML")
            return
        
        # Перевірка розміру файлу
        if message.document.file_size > 20 * 1024 * 1024:
            await message.answer("⚠️ <b>Файл занадто великий</b>\nМаксимальний розмір: 20 МБ", parse_mode="HTML")
            return
        
        # Сповіщення про отримання файлу
        await message.answer("📥 <b>Крок 5 з 5:</b> Отримую файл...", parse_mode="HTML")
        
        # Створення тимчасової директорії
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        # Створення унікального імені файлу
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        file_path = f"{TEMP_DIR}/{message.from_user.id}_{unique_id}{file_extension}"
        
        # Завантаження файлу
        try:
            await message.answer("📊 Аналізую файл...")
            file_info = await message.bot.get_file(message.document.file_id)
            await message.bot.download_file(file_info.file_path, file_path)
        except Exception as download_error:
            logger.error(f"Download error for user {message.from_user.id}: {str(download_error)}")
            await message.answer("⚠️ <b>Помилка завантаження файлу</b>\nСпробуйте надіслати файл ще раз.", parse_mode="HTML")
            return
        
        # Перевірка файлу
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            await message.answer("⚠️ <b>Файл порожній</b>\nНадішліть файл з вмістом.", parse_mode="HTML")
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        
        # Підрахунок символів
        await message.answer("🔢 Підраховую символи...")
        char_count = count_chars_in_file(file_path)
        
        if char_count is None or char_count == 0:
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file_read"][user_lang], parse_mode="HTML")
            return
        
        # Отримання моделі та розрахунок ціни
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        price = calculate_price(char_count, model)
        
        # Збереження даних
        await state.update_data(
            file_path=file_path,
            file_extension=file_extension,
            char_count=char_count,
            price=price
        )
        
        # Переходимо до наступного стану
        await TranslationStates.next()
        
        # Відправка статистики з кнопкою оплати
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Безпечне отримання назви моделі
        try:
            model_config = config.MODELS.get(model, config.MODELS["basic"])
            model_name = model_config["name"]
        except:
            model_name = "Kaminskyi Basic"
        
        stats_message = MESSAGES["file_stats"][user_lang].format(
            chars=char_count,
            model=model_name,
            price=price
        )
        
        await message.answer("💳 <b>Розрахунок вартості:</b>", parse_mode="HTML")
        await message.answer(stats_message, parse_mode="HTML")
        
        # СТВОРЮЄМО СПРАВЖНЮ КНОПКУ ОПЛАТИ
        try:
            # Створюємо сесію оплати
            payment_url = create_payment_session(price, message.from_user.id, char_count, model)
            
            if payment_url:
                # Створюємо клавіатуру з кнопкою оплати
                payment_keyboard = types.InlineKeyboardMarkup()
                payment_keyboard.add(types.InlineKeyboardButton("💳 Оплатити зараз", url=payment_url))
                payment_keyboard.add(types.InlineKeyboardButton("🔄 Завантажити інший файл", callback_data="upload_another"))
                payment_keyboard.add(types.InlineKeyboardButton("✅ Оплату здійснено", callback_data="payment_done"))
                
                await message.answer("Виберіть дію:", reply_markup=payment_keyboard)
            else:
                # Якщо не вдалося створити оплату, кнопка для тестування
                test_keyboard = types.InlineKeyboardMarkup()
                test_keyboard.add(types.InlineKeyboardButton("⏭ Продовжити без оплати (тест)", callback_data="payment_done"))
                test_keyboard.add(types.InlineKeyboardButton("🔄 Завантажити інший файл", callback_data="upload_another"))
                
                await message.answer("⚠️ Тимчасові проблеми з оплатою. Можете продовжити тестово:", reply_markup=test_keyboard)
                
        except Exception as payment_error:
            logger.error(f"Payment creation error for user {message.from_user.id}: {str(payment_error)}")
            # Резервна клавіатура
            backup_keyboard = types.InlineKeyboardMarkup()
            backup_keyboard.add(types.InlineKeyboardButton("⏭ Продовжити без оплати (тест)", callback_data="payment_done"))
            backup_keyboard.add(types.InlineKeyboardButton("🔄 Завантажити інший файл", callback_data="upload_another"))
            
            await message.answer("⚠️ Проблеми з системою оплати. Можете продовжити тестово:", reply_markup=backup_keyboard)
        
        log_user_action(message.from_user.id, "uploaded_file", 
                       f"chars: {char_count}, model: {model}, price: {price}€")
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in handle_file for user {message.from_user.id}: {str(e)}", exc_info=True)
        await message.answer("⚠️ <b>Критична помилка обробки</b>\nКоманда підтримки сповіщена.", parse_mode="HTML")

def register_handlers_file(dp):
    dp.register_message_handler(handle_file, content_types=["document"], 
                              state=TranslationStates.waiting_for_file)