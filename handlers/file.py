import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.file_utils import count_chars_in_file
from utils.payment_utils import calculate_price
from states import TranslationStates
from locales.messages import MESSAGES
from config import TEMP_DIR
from utils.logger import log_user_action, log_error
import logging

logger = logging.getLogger(__name__)

async def handle_file(message: types.Message, state: FSMContext):
    """ПОВНА, ПЕРЕВІРЕНА обробка файлу"""
    try:
        logger.info(f"File handler started for user {message.from_user.id}")
        
        # Перевірка наявності файлу
        if not message.document:
            logger.warning(f"No document in message from user {message.from_user.id}")
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file"][user_lang], parse_mode="HTML")
            return
        
        # Перевірка типу файлу
        file_extension = os.path.splitext(message.document.file_name)[1].lower()
        logger.info(f"File extension: {file_extension} for user {message.from_user.id}")
        
        if file_extension not in ['.txt', '.docx', '.pdf']:
            logger.warning(f"Unsupported file type {file_extension} from user {message.from_user.id}")
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file_type"][user_lang], parse_mode="HTML")
            return
        
        # Перевірка розміру файлу (максимум 20 МБ)
        if message.document.file_size > 20 * 1024 * 1024:  # 20 MB
            logger.warning(f"File too large ({message.document.file_size}) from user {message.from_user.id}")
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
        
        logger.info(f"Downloading file to {file_path} for user {message.from_user.id}")
        
        # Завантаження файлу
        try:
            await message.answer("📊 Аналізую файл...")
            file_info = await message.bot.get_file(message.document.file_id)
            await message.bot.download_file(file_info.file_path, file_path)
            logger.info(f"File downloaded successfully to {file_path}")
        except Exception as download_error:
            logger.error(f"Download error for user {message.from_user.id}: {str(download_error)}")
            await message.answer("⚠️ <b>Помилка завантаження файлу</b>\nСпробуйте надіслати файл ще раз.", parse_mode="HTML")
            return
        
        # Перевірка чи файл існує і не порожній
        if not os.path.exists(file_path):
            logger.error(f"File not found after download: {file_path} for user {message.from_user.id}")
            await message.answer("⚠️ <b>Файл не збережено</b>\nСпробуйте надіслати файл ще раз.", parse_mode="HTML")
            return
            
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.error(f"Downloaded file is empty: {file_path} for user {message.from_user.id}")
            await message.answer("⚠️ <b>Файл порожній</b>\nНадішліть файл з вмістом.", parse_mode="HTML")
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        
        logger.info(f"File size: {file_size} bytes for user {message.from_user.id}")
        
        # Підрахунок символів
        await message.answer("🔢 Підраховую символи...")
        char_count = count_chars_in_file(file_path)
        
        logger.info(f"Character count result: {char_count} for user {message.from_user.id}")
        
        if char_count is None or char_count == 0:
            logger.warning(f"Zero or None character count for file {file_path} from user {message.from_user.id}")
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file_read"][user_lang], parse_mode="HTML")
            # Не видаляємо файл для діагностики
            return
        
        # Отримання моделі та розрахунок ціни
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        price = calculate_price(char_count, model)
        
        logger.info(f"Price calculation: {char_count} chars, model {model}, price {price}€ for user {message.from_user.id}")
        
        # Збереження даних
        await state.update_data(
            file_path=file_path,
            file_extension=file_extension,
            char_count=char_count,
            price=price
        )
        
        # Переходимо до наступного стану
        await TranslationStates.next()
        
        # Відправка статистики
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
        
        log_user_action(message.from_user.id, "uploaded_file", 
                       f"chars: {char_count}, model: {model}, price: {price}€, size: {file_size}")
        
        logger.info(f"File handling completed successfully for user {message.from_user.id}")
        
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError for user {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ <b>Помилка файлу</b>\nФайл не знайдено. Спробуйте ще раз.", parse_mode="HTML")
    except PermissionError as e:
        logger.error(f"PermissionError for user {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ <b>Помилка доступу</b>\nНемає доступу до файлу.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"CRITICAL ERROR in handle_file for user {message.from_user.id}: {str(e)}", exc_info=True)
        await message.answer("⚠️ <b>Критична помилка обробки</b>\nКоманда підтримки сповіщена.", parse_mode="HTML")

def register_handlers_file(dp):
    dp.register_message_handler(handle_file, content_types=["document"], 
                              state=TranslationStates.waiting_for_file)