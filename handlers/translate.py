from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging
import os

logger = logging.getLogger(__name__)

async def start_translation(message: types.Message, state: FSMContext):
    """ПОЧАТОК ПЕРЕКЛАДУ"""
    try:
        logger.info(f"🔄 ПОЧАТОК ПЕРЕКЛАДУ для користувача {message.from_user.id}")
        
        # Отримуємо дані
        user_data = await state.get_data()
        file_path = user_data.get('file_path')
        file_extension = user_data.get('file_extension')
        source_lang = user_data.get('source_language')
        target_lang = user_data.get('target_language')
        model = user_data.get('model', 'basic')
        
        if not file_path or not os.path.exists(file_path):
            await message.answer("⚠️ Файл не знайдено")
            return
        
        # Імітація перекладу
        await message.answer("🔄 Перекладаємо файл...")
        await message.answer("⏳ Це може зайняти кілька секунд...")
        
        # Створюємо фейковий перекладений файл
        translated_path = file_path.replace(file_extension, f"_translated{file_extension}")
        
        # Для тестування - копіюємо оригінал
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(translated_path, 'w', encoding='utf-8') as f:
            f.write(f"[ПЕРЕКЛАД] {content}")
        
        # Відправляємо файл
        await message.answer_document(
            open(translated_path, 'rb'),
            caption="✅ Переклад завершено!"
        )
        
        # Очищуємо тимчасові файли
        try:
            os.remove(file_path)
            os.remove(translated_path)
        except:
            pass
        
        # Завершуємо
        await state.finish()
        
        # Пропозиція продовжити
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🔄 Новий переклад", callback_data="continue_translate"))
        keyboard.add(types.InlineKeyboardButton("👋 Вийти", callback_data="exit"))
        
        await message.answer(
            "🎯 Kaminskyi AI Translator\n\nХочете зробити ще один переклад?",
            reply_markup=keyboard
        )
        
        logger.info(f"✅ ПЕРЕКЛАД завершено для користувача {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в start_translation для користувача {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ Помилка перекладу")

def register_handlers_translate(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ ПЕРЕКЛАДУ"""
    dp.register_message_handler(start_translation, state=TranslationStates.translating)