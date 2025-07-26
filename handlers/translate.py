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
    """Оновлення повідомлення про прогрес"""
    try:
        progress_message = MESSAGES["translation_progress"][user_lang].format(
            model=model_name, 
            progress=progress
        )
        await message.edit_text(progress_message, parse_mode="HTML")
    except:
        pass  # Ігноруємо помилки оновлення

async def start_translation(message: types.Message, state: FSMContext):
    try:
        # Отримання даних користувача
        user_data = await state.get_data()
        file_path = user_data.get('file_path')
        file_extension = user_data.get('file_extension')
        source_lang = user_data.get('source_language')
        target_lang = user_data.get('target_language')
        char_count = user_data.get('char_count')
        model = user_data.get('model', 'basic')
        price = user_data.get('price')
        
        # Перевірка наявності файлу
        if not file_path or not os.path.exists(file_path):
            await message.answer("⚠️ <b>Файл не знайдено</b>\nСпробуйте завантажити файл ще раз.", parse_mode="HTML")
            return
        
        # Визначення мови користувача
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        model_name = config.MODELS[model]["name"]
        
        # Повідомлення про початок перекладу
        start_message = MESSAGES["translation_progress"][user_lang].format(
            model=model_name, 
            progress=0
        )
        progress_message = await message.answer(start_message, parse_mode="HTML")
        
        # Callback для оновлення прогресу
        async def update_progress(progress):
            await progress_callback(progress_message, user_lang, model_name, progress)
        
        # Переклад залежно від моделі
        try:
            if model == "basic":
                translated_file_path = await translate_basic(
                    file_path, source_lang, target_lang, file_extension, update_progress
                )
            else:  # epic
                await TranslationStates.waiting_for_otranslator_completion.set()
                waiting_message = MESSAGES["waiting_for_otranslator"][user_lang]
                await progress_message.edit_text(waiting_message, parse_mode="HTML")
                
                translated_file_path = await translate_epic(
                    file_path, source_lang, target_lang, file_extension, update_progress
                )
            
            # Відправка перекладеного файлу
            if os.path.exists(translated_file_path):
                await message.answer_document(
                    open(translated_file_path, 'rb'),
                    caption=MESSAGES["translation_completed"][user_lang],
                    parse_mode="HTML"
                )
                
                # Очищення тимчасових файлів
                cleanup_temp_file(file_path)
                cleanup_temp_file(translated_file_path)
            else:
                await message.answer("⚠️ <b>Помилка створення файлу</b>\nСпробуйте ще раз.", parse_mode="HTML")
                
            # Логування перекладу
            log_translation(message.from_user.id, model, char_count, price)
            
            # Пропозиція продовжити
            await state.finish()
            await message.answer(
                MESSAGES["thank_you"][user_lang],
                reply_markup=get_continue_keyboard(user_lang),
                parse_mode="HTML"
            )
            log_user_action(message.from_user.id, "translation_completed", 
                           f"model: {model}, chars: {char_count}")
            
        except Exception as e:
            # Обробка помилок перекладу
            log_error(e, f"Translation error for user {message.from_user.id}")
            await message.answer(f"⚠️ <b>Помилка перекладу:</b>\n{str(e)}", parse_mode="HTML")
            await state.finish()
            
    except Exception as e:
        log_error(e, f"Translation for user {message.from_user.id}")
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        await message.answer(MESSAGES["error_processing"][user_lang], parse_mode="HTML")
        await state.finish()

def register_handlers_translate(dp):
    dp.register_message_handler(start_translation, state=TranslationStates.translating)