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
    """Обробка отриманого файлу"""
    try:
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
        
        # Перевірка розміру файлу (максимум 20 МБ)
        if message.document.file_size > 20 * 1024 * 1024:  # 20 MB
            await message.answer("⚠️ <b>Файл занадто великий</b>\nМаксимальний розмір: 20 МБ", parse_mode="HTML")
            return
        
        await message.answer("📥 <b>Крок 5 з 5:</b> Отримую файл...", parse_mode="HTML")
        
        # Створення тимчасового файлу
        file_info = await message.bot.get_file(message.document.file_id)
        file_path = f"{TEMP_DIR}/{message.from_user.id}_{message.document.file_id}{file_extension}"
        
        # Завантаження файлу
        await message.answer("📊 Аналізую файл...")
        await message.bot.download_file(file_info.file_path, file_path)
        
        # Підрахунок символів з детальною інформацією
        char_count = count_chars_in_file(file_path)
        
        if char_count == 0:
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file_read"][user_lang], parse_mode="HTML")
            if os.path.exists(file_path):
                os.remove(file_path)
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
        
        # Відправка статистики
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        model_name = config.MODELS.get(model, config.MODELS["basic"])["name"]
        stats_message = MESSAGES["file_stats"][user_lang].format(
            chars=char_count,
            model=model_name,
            price=price
        )
        
        await message.answer("💳 <b>Розрахунок вартості:</b>", parse_mode="HTML")
        await message.answer(stats_message, parse_mode="HTML")
        log_user_action(message.from_user.id, "uploaded_file", 
                       f"chars: {char_count}, model: {model}, price: {price}€")
        
    except FileNotFoundError as e:
        logger.error(f"File not found error for user {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ <b>Помилка файлу</b>\nФайл не знайдено. Спробуйте ще раз.", parse_mode="HTML")
    except PermissionError as e:
        logger.error(f"Permission error for user {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ <b>Помилка доступу</b>\nНемає доступу до файлу. Спробуйте ще раз.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error handling file for user {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ <b>Помилка обробки файлу</b>\nСталася неочікувана помилка. Спробуйте ще раз.", parse_mode="HTML")

def register_handlers_file(dp):
    dp.register_message_handler(handle_file, content_types=["document"], 
                              state=TranslationStates.waiting_for_file)