import os
import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from models.basic import translate_basic
from models.epic import translate_epic
from states import TranslationStates
from keyboards.inline import get_continue_keyboard
from locales.messages import MESSAGES
from utils.logger import log_user_action, log_error, log_translation
from utils.file_utils import cleanup_temp_file
import logging

logger = logging.getLogger(__name__)

async def progress_callback(message: types.Message, user_lang: str, model_name: str, progress: int):
    """Update progress message"""
    try:
        await message.edit_text(
            MESSAGES["translation_progress"][user_lang].format(model=model_name, progress=progress)
        )
    except:
        pass  # Ignore errors in progress updates

async def start_translation(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        file_path = user_data.get('file_path')
        file_extension = user_data.get('file_extension')
        source_lang = user_data.get('source_language')
        target_lang = user_data.get('target_language')
        char_count = user_data.get('char_count')
        model = user_data.get('model', 'basic')
        price = user_data.get('price')
        
        if not file_path or not os.path.exists(file_path):
            await message.answer("⚠️ Файл не знайдено")
            return
        
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        model_name = config.MODELS[model]["name"]
        
        # Show initial progress
        progress_message = await message.answer(
            MESSAGES["translation_progress"][user_lang].format(model=model_name, progress=0)
        )
        
        # Define progress callback
        async def update_progress(progress):
            await progress_callback(progress_message, user_lang, model_name, progress)
        
        # Translate based on model
        if model == "basic":
            translated_file_path = await translate_basic(
                file_path, source_lang, target_lang, file_extension, update_progress
            )
        else:  # epic
            await TranslationStates.waiting_for_otranslator_completion.set()
            await progress_message.edit_text(MESSAGES["waiting_for_otranslator"][user_lang])
            
            translated_file_path = await translate_epic(
                file_path, source_lang, target_lang, file_extension, update_progress
            )
        
        # Send translated file
        if os.path.exists(translated_file_path):
            await message.answer_document(
                open(translated_file_path, 'rb'),
                caption=MESSAGES["translation_completed"][user_lang]
            )
            
            # Clean up files
            cleanup_temp_file(file_path)
            cleanup_temp_file(translated_file_path)
        else:
            await message.answer("⚠️ Помилка при створенні перекладеного файлу")
            
        # Log translation
        log_translation(message.from_user.id, model, char_count, price)
        
        # Offer to continue
        await state.finish()
        await message.answer(
            MESSAGES["thank_you"][user_lang],
            reply_markup=get_continue_keyboard(user_lang)
        )
        log_user_action(message.from_user.id, "translation_completed", 
                       f"model: {model}, chars: {char_count}")
        
    except Exception as e:
        log_error(e, f"Translation for user {message.from_user.id}")
        await message.answer(f"⚠️ Помилка перекладу: {str(e)}")
        await state.finish()

def register_handlers_translate(dp):
    dp.register_message_handler(start_translation, state=TranslationStates.translating)