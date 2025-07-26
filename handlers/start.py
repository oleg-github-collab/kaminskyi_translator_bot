from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """СТАРТ БОТА"""
    try:
        logger.info(f"START для користувача {message.from_user.id}")
        
        # ПОВНЕ СКИДАННЯ
        await state.finish()
        await state.reset_data()
        
        # Встановлюємо початковий стан
        await TranslationStates.choosing_model.set()
        
        # Відправляємо привітання з описом моделей
        welcome_message = "🎯 <b>Kaminskyi AI Translator</b>\n\n"
        welcome_message += "⚡ <b>Basic</b> - швидкий переклад через DeepL\n"
        welcome_message += "🎯 <b>Epic</b> - якість через Gemini 2.5 Flash\n\n"
        welcome_message += "<b>Крок 1/5:</b> Оберіть модель перекладу:"
        
        await message.answer(welcome_message, parse_mode="HTML")
        
        # Створюємо кнопки моделей прямо тут
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
            types.InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
        )
        
        await message.answer("Виберіть модель:", reply_markup=keyboard)
        
        logger.info(f"START успішний для користувача {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в cmd_start: {str(e)}")
        await message.answer("⚠️ Помилка. Спробуйте /start")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОДЕЛІ - з фільтром"""
    try:
        logger.info(f"ВИБІР МОДЕЛІ: {callback.data} для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data:
            await callback.answer("⚠️ Помилка даних")
            return
            
        if not callback.data.startswith("model_"):
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        
        # Отримуємо модель
        model = callback.data.split("_")[1]
        await state.update_data(model=model)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_source_language
        
        # Відправляємо вибір мови оригіналу з кнопками
        await callback.message.answer("<b>Крок 2/5:</b> Оберіть мову оригіналу:", parse_mode="HTML")
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_UK"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_EN")
        )
        keyboard.add(
            types.InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_DE"),
            types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_FR")
        )
        keyboard.add(
            types.InlineKeyboardButton("🇪🇸 Español", callback_data="lang_ES"),
            types.InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_PL")
        )
        
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        logger.info(f"МОДЕЛЬ {model} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_model: {str(e)}")
        await callback.answer("⚠️ Помилка вибору")

async def continue_translate(callback: types.CallbackQuery, state: FSMContext):
    """ПРОДОВЖЕННЯ ПЕРЕКЛАДУ"""
    try:
        await callback.answer()
        
        # Повне скидання
        await state.finish()
        await state.reset_data()
        await TranslationStates.choosing_model.set()
        
        # Новий старт
        welcome_message = "🎯 <b>Kaminskyi AI Translator</b>\n\n<b>Крок 1/5:</b> Новий переклад:"
        await callback.message.answer(welcome_message, parse_mode="HTML")
        
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
            types.InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
        )
        
        await callback.message.answer("Виберіть модель:", reply_markup=keyboard)
        
        logger.info(f"ПРОДОВЖЕННЯ для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в continue_translate: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def exit_bot(callback: types.CallbackQuery, state: FSMContext):
    """ВИХІД З БОТА"""
    try:
        await callback.answer()
        await state.finish()
        await state.reset_data()
        
        await callback.message.answer("👋 Дякуємо! Повертайтесь: /start")
        logger.info(f"ВИХІД для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в exit_bot: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def upload_another(callback: types.CallbackQuery, state: FSMContext):
    """ЗАВАНТАЖИТИ ІНШИЙ ФАЙЛ"""
    try:
        await callback.answer()
        
        # Повертаємося до стану очікування файлу
        await TranslationStates.waiting_for_file.set()
        
        await callback.message.answer("📥 Надішліть інший файл для перекладу (txt, docx, pdf)")
        logger.info(f"ІНШИЙ ФАЙЛ для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в upload_another: {str(e)}")
        await callback.answer("⚠️ Помилка")

def register_handlers_start(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ - правильний порядок"""
    # Старт в будь-якому стані
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    
    # Вибір моделі - з фільтром
    dp.register_callback_query_handler(choose_model, lambda c: c.data and c.data.startswith("model_"))
    
    # Продовження
    dp.register_callback_query_handler(continue_translate, lambda c: c.data and c.data == "continue_translate")
    
    # Вихід
    dp.register_callback_query_handler(exit_bot, lambda c: c.data and c.data == "exit")
    
    # Інший файл
    dp.register_callback_query_handler(upload_another, lambda c: c.data and c.data == "upload_another")