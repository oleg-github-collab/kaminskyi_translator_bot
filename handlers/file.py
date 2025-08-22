from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from utils.file_validation import comprehensive_file_validation, create_validation_report, get_supported_formats_text
from utils.language_system import get_language_name
from utils.simple_debug import debug_callback, log_action
import logging
import os

logger = logging.getLogger(__name__)

@debug_callback
async def handle_file(message: types.Message, state: FSMContext):
    """🚀 УЛЬТРАПОТУЖНА ОБРОБКА ФАЙЛУ З ПОВНОЮ ВАЛІДАЦІЄЮ"""
    user_id = message.from_user.id
    log_action("file_upload_start", user_id, "processing file")
    
    try:
        logger.info(f"📁 УЛЬТРА ОБРОБКА ФАЙЛУ від користувача {user_id}")
        
        # 1. ПЕРЕВІРКА НАЯВНОСТІ ФАЙЛУ
        if not message.document:
            logger.warning(f"⚠️ Немає файлу від користувача {user_id}")
            await message.answer(
                "⚠️ **Файл не знайдено**\n\n" + get_supported_formats_text(),
                parse_mode="Markdown"
            )
            return
        
        # 2. ПОЧАТКОВА ПЕРЕВІРКА РОЗМІРУ
        file_size_mb = message.document.file_size / 1024 / 1024 if message.document.file_size else 0
        logger.info(f"📊 Розмір файлу: {file_size_mb:.2f} MB")
        
        if message.document.file_size and message.document.file_size > 500 * 1024 * 1024:  # 500MB
            await message.answer(
                f"❌ **Файл занадто великий**\n\n"
                f"Розмір: {file_size_mb:.1f} MB\n"
                f"Максимум: 500 MB\n\n"
                + get_supported_formats_text(),
                parse_mode="Markdown"
            )
            return
        
        # 3. ПОКАЗУЄМО ПРОЦЕС
        processing_msg = await message.answer("🔄 **Обробляю файл...**", parse_mode="Markdown")
        
        # 4. СТВОРЕННЯ БЕЗПЕЧНОГО ШЛЯХУ
        os.makedirs('temp', exist_ok=True)
        safe_filename = f"{user_id}_{message.document.file_id}_{message.document.file_name}"
        file_path = os.path.join('temp', safe_filename)
        
        # 5. ЗАВАНТАЖЕННЯ ФАЙЛУ
        try:
            await processing_msg.edit_text("⬇️ **Завантажую файл...**", parse_mode="Markdown")
            file_info = await message.bot.get_file(message.document.file_id)
            await message.bot.download_file(file_info.file_path, file_path)
            logger.info(f"✅ Файл завантажено: {file_path}")
        except Exception as e:
            logger.error(f"❌ Помилка завантаження файлу: {e}")
            await processing_msg.edit_text("❌ **Помилка завантаження файлу**", parse_mode="Markdown")
            return
        
        # 6. УЛЬТРА ВАЛІДАЦІЯ
        await processing_msg.edit_text("🔍 **Аналізую файл...**", parse_mode="Markdown")
        validation_result = comprehensive_file_validation(file_path, message.document.file_name)
        
        # 7. ПЕРЕВІРКА РЕЗУЛЬТАТУ ВАЛІДАЦІЇ
        if not validation_result.is_valid:
            # Очищуємо файл
            try:
                os.remove(file_path)
            except:
                pass
            
            await processing_msg.edit_text(
                f"❌ **Валідація не пройдена**\n\n{validation_result.error_message}\n\n" + get_supported_formats_text(),
                parse_mode="Markdown"
            )
            log_action("file_validation_failed", user_id, validation_result.error_message)
            return
        
        # 8. ОТРИМАННЯ ДАНИХ КОРИСТУВАЧА
        user_data = await state.get_data()
        source_lang = user_data.get('source_language', 'UK')
        target_lang = user_data.get('target_language', 'EN') 
        model = user_data.get('model', 'basic')
        
        # 9. РОЗРАХУНОК ТОЧНОЇ ВАРТОСТІ
        await processing_msg.edit_text("💰 **Розраховую вартість...**", parse_mode="Markdown")
        from utils.file_validation import PRICING
        price_per_char = PRICING.get(model, PRICING['basic'])
        total_cost = validation_result.char_count * price_per_char
        
        # 10. ЗБЕРЕЖЕННЯ ДАНИХ
        await state.update_data(
            file_path=file_path,
            file_extension=validation_result.extension,
            file_size=validation_result.size_bytes,
            char_count=validation_result.char_count,
            estimated_cost=total_cost,
            processing_time=validation_result.processing_time_estimate,
            file_validated=True
        )
        
        # 11. ПЕРЕХІД ДО ОПЛАТИ
        await TranslationStates.waiting_for_payment_confirmation.set()
        
        # 12. ВІДОБРАЖЕННЯ РЕЗУЛЬТАТІВ
        await processing_msg.delete()
        
        # Інформація про переклад
        source_name = get_language_name(source_lang)
        target_name = get_language_name(target_lang)
        model_name = "Kaminskyi Basic" if model == "basic" else "Kaminskyi Epic"
        
        await message.answer(
            f"✅ **Файл успішно оброблено!**\n\n"
            f"📄 **Файл:** {message.document.file_name}\n"
            f"🔤 **Переклад:** {source_name} → {target_name}\n"
            f"⚙️ **Модель:** {model_name}",
            parse_mode="Markdown"
        )
        
        # Детальний звіт валідації
        report = create_validation_report(validation_result)
        await message.answer(report, parse_mode="Markdown")
        
        # Попередження якщо є
        if validation_result.warnings:
            warning_text = "⚠️ **Попередження:**\n" + "\n".join(f"• {w}" for w in validation_result.warnings)
            await message.answer(warning_text, parse_mode="Markdown")
        
        # Кнопки дій
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💳 Оплатити переклад", callback_data="process_payment"))
        keyboard.add(
            types.InlineKeyboardButton("🔄 Інший файл", callback_data="upload_another"),
            types.InlineKeyboardButton("ℹ️ Допомога", callback_data="payment_help")
        )
        
        await message.answer("**Оберіть дію:**", reply_markup=keyboard, parse_mode="Markdown")
        
        log_action("file_upload_success", user_id, f"{validation_result.char_count:,} chars, {total_cost:.2f}€")
        logger.info(f"✅ УЛЬТРА ФАЙЛ оброблено для користувача {user_id}: {validation_result.char_count:,} символів")
        
    except Exception as e:
        log_action("file_upload_error", user_id, str(e))
        logger.error(f"❌ КРИТИЧНА ПОМИЛКА в handle_file для користувача {user_id}: {str(e)}")
        
        # Очищення файлу при помилці
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
            
        await message.answer(
            "❌ **Критична помилка обробки файлу**\n\n"
            "Спробуйте:\n"
            "• Перевірити формат файлу\n"
            "• Зменшити розмір файлу\n"
            "• Надіслати файл знову\n\n"
            + get_supported_formats_text(),
            parse_mode="Markdown"
        )

def register_handlers_file(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ ФАЙЛУ"""
    dp.register_message_handler(handle_file, content_types=["document"], state=TranslationStates.waiting_for_file)