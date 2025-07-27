from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging
from utils.file_utils import count_chars_in_file
from utils.payment_utils import calculate_price
import os

logger = logging.getLogger(__name__)

async def handle_file(message: types.Message, state: FSMContext):
    """ОБРОБКА ФАЙЛУ"""
    try:
        logger.info(f"📁 ОБРОБКА ФАЙЛУ від користувача {message.from_user.id}")
        
        # Перевірка наявності файлу
        if not message.document:
            logger.warning(f"⚠️ Немає файлу від користувача {message.from_user.id}")
            await message.answer("⚠️ Надішліть файл (txt, docx, pdf)")
            return
        
        # Перевірка типу файлу
        file_extension = os.path.splitext(message.document.file_name)[1].lower()
        if file_extension not in ['.txt', '.docx', '.pdf']:
            logger.warning(f"⚠️ Непідтримуваний тип файлу {file_extension} від користувача {message.from_user.id}")
            await message.answer("⚠️ Підтримуються лише: txt, docx, pdf")
            return
        
        # Створення тимчасового файлу
        os.makedirs('temp', exist_ok=True)
        file_path = f"temp/{message.from_user.id}_{message.document.file_id}{file_extension}"
        
        # Завантаження файлу
        file_info = await message.bot.get_file(message.document.file_id)
        await message.bot.download_file(file_info.file_path, file_path)
        
        # Збереження даних
        await state.update_data(file_path=file_path, file_extension=file_extension)
        
        # Переходимо до оплати
        await TranslationStates.waiting_for_payment_confirmation.set()
        
        # Відображаємо інформацію
        user_data = await state.get_data()
        source_lang = user_data.get('source_language', 'UK')
        target_lang = user_data.get('target_language', 'EN')
        model = user_data.get('model', 'basic')
        
        from handlers.language import get_language_name
        source_name = get_language_name(source_lang)
        target_name = get_language_name(target_lang)
        model_name = "Kaminskyi Basic" if model == "basic" else "Kaminskyi Epic"
        
        await message.answer(f"📄 Файл отримано!")
        await message.answer(f"🔤 Переклад: {source_name} → {target_name}")
        await message.answer(f"⚙️ Модель: {model_name}")
        
        # Аналіз файлу
        await message.answer("📊 Аналізую файл...")
        char_count = count_chars_in_file(file_path)
        price = calculate_price(char_count, model)
        await state.update_data(char_count=char_count, price=price)

        # Відображаємо статистику
        await message.answer("💳 <b>Розрахунок вартості:</b>", parse_mode="HTML")
        await message.answer(f"• Символів: {char_count}\n• Вартість: {price} €")
        
        # Кнопки оплати
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💳 Оплатити", callback_data="process_payment"))
        keyboard.add(types.InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"))
        
        await message.answer("Виберіть дію:", reply_markup=keyboard)
        
        logger.info(f"✅ ФАЙЛ оброблено для користувача {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_file для користувача {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ Помилка обробки файлу")

def register_handlers_file(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ ФАЙЛУ"""
    dp.register_message_handler(handle_file, content_types=["document"], state=TranslationStates.waiting_for_file)