from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging
import os
from models import translate_basic, translate_epic
from utils.logger import log_translation, log_error

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
        char_count = user_data.get('char_count', 0)
        price = user_data.get('price', 0.0)
        logger.debug(
            f"Translation params for {message.from_user.id}: file={file_path}, src={source_lang}, tgt={target_lang}, model={model}, chars={char_count}, price={price}"
        )
        
        if not file_path or not os.path.exists(file_path):
            await message.answer("⚠️ Файл не знайдено")
            return
        
        progress_msg = await message.answer("🔄 Перекладаємо файл... 0%")

        async def progress(percent: int):
            try:
                await progress_msg.edit_text(f"🔄 Перекладаємо файл... {percent}%")
            except Exception:
                pass

        if model == 'basic':
            translated_path = await translate_basic(
                file_path, source_lang, target_lang, file_extension, progress
            )
        else:
            translated_path = await translate_epic(
                file_path, source_lang, target_lang, file_extension, progress
            )

        # Імітація перекладу
        await message.answer("🔄 Перекладаємо файл...")
        await message.answer("⏳ Це може зайняти кілька секунд...")
        
        # Створюємо фейковий перекладений файл
        translated_path = file_path.replace(file_extension, f"_translated{file_extension}")
        
        # Для тестування - копіюємо оригінал
        with open(file_path, 'rb') as f:
            raw = f.read()
        try:
            content = raw.decode('utf-8')
        except Exception:
            content = raw.decode('utf-8', errors='ignore')
        
        with open(translated_path, 'wb') as f:
            f.write(f"[ПЕРЕКЛАД] {content}".encode('utf-8'))
        
        try:
            await progress_msg.edit_text("✅ Переклад завершено!")
        except Exception:
            pass

        try:
            await progress_msg.delete()
        except Exception:
            pass

        await message.answer_document(
            open(translated_path, 'rb'),
            caption="✅ Переклад завершено!"
        )
        log_translation(message.from_user.id, model, char_count, price)
        
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
        logger.error(
            f"❌ ПОМИЛКА в start_translation для користувача {message.from_user.id}: {str(e)}"
        )
        log_error(e, "start_translation")
        await message.answer("⚠️ Помилка перекладу")

def register_handlers_translate(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ ПЕРЕКЛАДУ"""
    dp.register_message_handler(start_translation, state=TranslationStates.translating)
