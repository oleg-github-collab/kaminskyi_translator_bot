import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.file_utils import count_chars_in_file
from utils.payment_utils import calculate_price, create_payment_session
from states import TranslationStates
from locales.messages import MESSAGES
from config import TEMP_DIR
from utils.logger import log_user_action, log_error
from keyboards.inline import get_file_action_keyboard
import logging

logger = logging.getLogger(__name__)

async def handle_file(message: types.Message, state: FSMContext):
    """МАКСИМАЛЬНО НАДІЙНА обробка файлу"""
    try:
        logger.info(f"=== ПОЧАТОК ОБРОБКИ ФАЙЛУ === User: {message.from_user.id}")
        
        # Перевірка наявності файлу
        if not message.document:
            logger.warning(f"Немає документа від користувача {message.from_user.id}")
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer("⚠️ <b>Помилка</b>\nНадішліть файл (txt, docx, pdf)", parse_mode="HTML")
            return
        
        # Перевірка типу файлу
        file_extension = os.path.splitext(message.document.file_name)[1].lower()
        logger.info(f"Тип файлу: {file_extension} для користувача {message.from_user.id}")
        
        if file_extension not in ['.txt', '.docx', '.pdf']:
            logger.warning(f"Непідтримуваний тип файлу {file_extension} від користувача {message.from_user.id}")
            await message.answer("⚠️ <b>Непідтримуваний формат</b>\nПідтримуються: TXT, DOCX, PDF", parse_mode="HTML")
            return
        
        # Перевірка розміру файлу
        if message.document.file_size > 20 * 1024 * 1024:  # 20 MB
            logger.warning(f"Файл занадто великий ({message.document.file_size}) для користувача {message.from_user.id}")
            await message.answer("⚠️ <b>Файл занадто великий</b>\nМаксимальний розмір: 20 МБ", parse_mode="HTML")
            return
        
        # Сповіщення про отримання файлу
        await message.answer("📥 <b>Крок 5/5:</b> Отримую файл...", parse_mode="HTML")
        logger.info(f"Починаємо завантаження файлу для користувача {message.from_user.id}")
        
        # Створення тимчасової директорії
        os.makedirs(TEMP_DIR, exist_ok=True)
        logger.info(f"Директорія {TEMP_DIR} готова")
        
        # Створення унікального імені файлу
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        file_path = f"{TEMP_DIR}/{message.from_user.id}_{unique_id}{file_extension}"
        logger.info(f"Шлях файлу: {file_path}")
        
        # Завантаження файлу з повторними спробами
        try:
            await message.answer("📊 Аналізую файл...")
            file_info = await message.bot.get_file(message.document.file_id)
            await message.bot.download_file(file_info.file_path, file_path)
            logger.info(f"Файл успішно завантажено для користувача {message.from_user.id}")
        except Exception as download_error:
            logger.error(f"Помилка завантаження для користувача {message.from_user.id}: {str(download_error)}")
            await message.answer("⚠️ <b>Помилка завантаження</b>\nСпробуйте надіслати файл ще раз.", parse_mode="HTML")
            return
        
        # Перевірка файлу
        if not os.path.exists(file_path):
            logger.error(f"Файл не існує після завантаження: {file_path} для користувача {message.from_user.id}")
            await message.answer("⚠️ <b>Файл не збережено</b>\nСпробуйте ще раз.", parse_mode="HTML")
            return
            
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.error(f"Файл порожній: {file_path} для користувача {message.from_user.id}")
            await message.answer("⚠️ <b>Файл порожній</b>\nНадішліть файл з вмістом.", parse_mode="HTML")
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        
        logger.info(f"Розмір файлу: {file_size} байт для користувача {message.from_user.id}")
        
        # Підрахунок символів
        await message.answer("🔢 Підраховую символи...")
        char_count = count_chars_in_file(file_path)
        
        logger.info(f"Підраховано символів: {char_count} для користувача {message.from_user.id}")
        
        if char_count is None or char_count == 0:
            logger.warning(f"Нульова кількість символів для файлу {file_path} користувача {message.from_user.id}")
            await message.answer("⚠️ <b>Файл порожній або пошкоджений</b>\nСпробуйте інший файл.", parse_mode="HTML")
            # Не видаляємо файл для діагностики
            return
        
        # Отримання моделі та розрахунок ціни
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        price = calculate_price(char_count, model)
        
        logger.info(f"Ціна: {price}€ для {char_count} символів, модель: {model} для користувача {message.from_user.id}")
        
        # Збереження даних
        await state.update_data(
            file_path=file_path,
            file_extension=file_extension,
            char_count=char_count,
            price=price
        )
        
        # Переходимо до наступного стану
        await TranslationStates.next()
        logger.info(f"Стан змінено на waiting_for_payment_confirmation для користувача {message.from_user.id}")
        
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
            logger.info(f"Створюємо сесію оплати для користувача {message.from_user.id}")
            payment_url = create_payment_session(price, message.from_user.id, char_count, model)
            
            if payment_url:
                logger.info(f"Сесія оплати створена успішно для користувача {message.from_user.id}")
                # Створюємо клавіатуру з кнопкою оплати
                payment_keyboard = types.InlineKeyboardMarkup()
                payment_keyboard.add(types.InlineKeyboardButton("💳 Оплатити зараз", url=payment_url))
                payment_keyboard.add(types.InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
                
                await message.answer("Виберіть дію:", reply_markup=payment_keyboard)
            else:
                logger.warning(f"Не вдалося створити сесію оплати для користувача {message.from_user.id}")
                # Резервна клавіатура
                backup_keyboard = get_file_action_keyboard()
                await message.answer("⚠️ Тимчасові проблеми з оплатою:", reply_markup=backup_keyboard)
                
        except Exception as payment_error:
            logger.error(f"Критична помилка оплати для користувача {message.from_user.id}: {str(payment_error)}", exc_info=True)
            # Резервна клавіатура
            backup_keyboard = get_file_action_keyboard()
            await message.answer("⚠️ Проблеми з оплатою:", reply_markup=backup_keyboard)
        
        log_user_action(message.from_user.id, "uploaded_file", 
                       f"chars: {char_count}, model: {model}, price: {price}€, size: {file_size}")
        logger.info(f"=== ОБРОБКУ ФАЙЛУ ЗАВЕРШЕНО УСПІШНО === User: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в handle_file для користувача {message.from_user.id}: {str(e)}", exc_info=True)
        await message.answer("⚠️ <b>Критична помилка</b>\nКоманда підтримки сповіщена.", parse_mode="HTML")

def register_handlers_file(dp):
    dp.register_message_handler(handle_file, content_types=["document"], 
                              state=TranslationStates.waiting_for_file)