from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging

logger = logging.getLogger(__name__)

# Helper функція для отримання назви мови
def _get_language_name(lang_code):
    """Отримання назви мови за кодом"""
    languages = {
        "UK": "Українська",
        "EN": "English", 
        "DE": "Deutsch",
        "FR": "Français",
        "ES": "Español",
        "PL": "Polski"
    }
    return languages.get(lang_code, lang_code)

async def handle_file(message: types.Message, state: FSMContext):
    """ОБРОБКА ФАЙЛУ"""
    try:
        logger.info(f"ОБРОБКА ФАЙЛУ для користувача {message.from_user.id}")
        
        # Перевірка наявності файлу
        if not message.document:
            await message.answer("⚠️ Надішліть файл (txt, docx, pdf)")
            return
        
        # Перевірка типу файлу
        file_extension = message.document.file_name.split('.')[-1].lower()
        if file_extension not in ['txt', 'docx', 'pdf']:
            await message.answer("⚠️ Підтримуються лише: txt, docx, pdf")
            return
        
        # Відображаємо вибрані мови
        user_data = await state.get_data()
        source_lang = user_data.get('source_language', 'UK')
        target_lang = user_data.get('target_language', 'EN')
        
        source_name = _get_language_name(source_lang)
        target_name = _get_language_name(target_lang)
        
        await message.answer(f"📄 Файл отримано!")
        await message.answer(f"🔤 Переклад: {source_name} → {target_name}")
        
        # Імітація обробки
        await message.answer("📊 Аналізую файл...")
        await message.answer("🔢 Підраховую символи...")
        
        # Переходимо до оплати
        await TranslationStates.waiting_for_payment_confirmation.set()
        
        # Відображаємо статистику
        await message.answer("💳 <b>Розрахунок вартості:</b>", parse_mode="HTML")
        await message.answer("• Символів: 514\n• Вартість: 0.65 €")
        
        # Кнопки оплати
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
        keyboard.add(types.InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
        
        await message.answer("Виберіть дію:", reply_markup=keyboard)
        
        logger.info(f"ФАЙЛ ОБРОБЛЕНО для користувача {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в handle_file: {str(e)}")
        await message.answer("⚠️ Помилка обробки файлу")

def register_handlers_file(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ ФАЙЛУ"""
    dp.register_message_handler(handle_file, content_types=["document"], state=TranslationStates.waiting_for_file)