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
    try:
        if not message.document:
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file"][user_lang])
            return
        
        file_extension = os.path.splitext(message.document.file_name)[1].lower()
        if file_extension not in ['.txt', '.docx', '.pdf']:
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file_type"][user_lang])
            return
        
        # Create temporary file
        file_info = await message.bot.get_file(message.document.file_id)
        file_path = f"{TEMP_DIR}/{message.from_user.id}_{message.document.file_id}{file_extension}"
        
        # Download file
        await message.bot.download_file(file_info.file_path, file_path)
        
        # Count characters
        char_count = count_chars_in_file(file_path)
        if char_count == 0:
            user_lang = message.from_user.language_code or "en"
            user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
            await message.answer(MESSAGES["error_file_read"][user_lang])
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        
        # Get model and calculate price
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        price = calculate_price(char_count, model)
        
        await state.update_data(
            file_path=file_path,
            file_extension=file_extension,
            char_count=char_count,
            price=price
        )
        
        await TranslationStates.next()
        
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        model_name = config.MODELS[model]["name"]
        stats_message = MESSAGES["file_stats"][user_lang].format(
            chars=char_count,
            model=model_name,
            price=price
        )
        
        await message.answer(stats_message)
        log_user_action(message.from_user.id, "uploaded_file", 
                       f"chars: {char_count}, model: {model}, price: {price}€")
        
    except Exception as e:
        log_error(e, f"File handling for user {message.from_user.id}")
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        await message.answer("⚠️ Виникла помилка при обробці файлу. Спробуйте ще раз.")

def register_handlers_file(dp):
    dp.register_message_handler(handle_file, content_types=["document"], 
                              state=TranslationStates.waiting_for_file)