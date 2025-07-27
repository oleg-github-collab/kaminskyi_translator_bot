from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from handlers.language import build_language_keyboard
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """ПОЧАТОК РОБОТИ"""
    try:
        logger.info(f"🟢 START від користувача {message.from_user.id}")
        
        # ПОВНЕ СКИДАННЯ
        await state.finish()
        await state.reset_data()
        
        # Встановлюємо початковий стан
        await TranslationStates.choosing_model.set()
        
        # Відправляємо привітання
        welcome_message = (
            "🎯 <b>Kaminskyi AI Translator</b>\n\n"
            "⚡ Швидкий та якісний переклад файлів\n"
            "📄 Підтримка: TXT, DOCX, PDF\n"
            "💰 Вигідні ціни\n\n"
            "<b>Крок 1/5:</b> Оберіть модель перекладу:"
        )
        await message.answer(welcome_message, parse_mode="HTML")
        
        # Кнопки моделей - СТВОРЮЄМО ПРЯМО ТУТ
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
            types.InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
        )
        
        await message.answer("Виберіть модель:", reply_markup=keyboard)
        
        logger.info(f"✅ START успішний для користувача {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в cmd_start для користувача {message.from_user.id}: {str(e)}")
        await message.answer("⚠️ Помилка. Спробуйте /start")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОДЕЛІ - ЦЕ ГОЛОВНИЙ HANDLER"""
    try:
        logger.info(f"🔵 ВИБІР МОДЕЛІ: {callback.data} для користувача {callback.from_user.id}")
        print(f"DEBUG: ВИБІР МОДЕЛІ ВИКЛИКАНО: {callback.data}")  # ДЕБАГ
        
        # Перевірка даних
        if not callback.data:
            logger.warning(f"⚠️ ПУСТІ ДАНІ від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Помилка даних")
            return
            
        if not callback.data.startswith("model_"):
            logger.warning(f"⚠️ НЕПРАВИЛЬНІ ДАНІ: {callback.data} від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        
        # Отримуємо модель
        model = callback.data.split("_")[1]  # model_basic або model_epic
        await state.update_data(model=model)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_source_language
        
        # Відправляємо вибір мови оригіналу
        await callback.message.answer("<b>Крок 2/5:</b> Оберіть мову оригіналу:", parse_mode="HTML")
        
        # Динамічні кнопки мов
        keyboard = build_language_keyboard()
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        logger.info(f"✅ МОДЕЛЬ {model} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в choose_model для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка вибору")

async def continue_translate(callback: types.CallbackQuery, state: FSMContext):
    """ПРОДОВЖЕННЯ ПЕРЕКЛАДУ"""
    try:
        logger.info(f"🔄 ПРОДОВЖЕННЯ для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Повне скидання
        await state.finish()
        await state.reset_data()
        await TranslationStates.choosing_model.set()
        
        # Новий старт
        welcome_message = (
            "🎯 <b>Kaminskyi AI Translator</b>\n\n"
            "<b>Крок 1/5:</b> Новий переклад:"
        )
        await callback.message.answer(welcome_message, parse_mode="HTML")
        
        # Кнопки моделей - СТВОРЮЄМО ПРЯМО ТУТ
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
            types.InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
        )
        
        await callback.message.answer("Виберіть модель:", reply_markup=keyboard)
        
        logger.info(f"✅ ПРОДОВЖЕННЯ успішне для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в continue_translate для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

async def exit_bot(callback: types.CallbackQuery, state: FSMContext):
    """ВИХІД З БОТА"""
    try:
        logger.info(f"🚪 ВИХІД для користувача {callback.from_user.id}")
        await callback.answer()
        await state.finish()
        await state.reset_data()
        
        await callback.message.answer("👋 Дякуємо! Повертайтесь: /start")
        logger.info(f"✅ ВИХІД успішний для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в exit_bot для користувача {callback.from_user.id}: {str(e)}")
        await callback.answer("⚠️ Помилка")

def register_handlers_start(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ - КЛЮЧОВЕ ВИПРАВЛЕННЯ"""
    logger.info("=== РЕЄСТРАЦІЯ HANDLER'ІВ START ===")
    
    # Старт в будь-якому стані
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    logger.info("✅ Зареєстровано cmd_start")
    
    # Вибір моделі
    dp.register_callback_query_handler(
        choose_model,
        lambda c: c.data and c.data.startswith("model_"),
        state=TranslationStates.choosing_model,
    )
    logger.info("✅ Зареєстровано choose_model")
    
    # Продовження
    dp.register_callback_query_handler(continue_translate, lambda c: c.data and c.data == "continue_translate")
    logger.info("✅ Зареєстровано continue_translate")
    
    # Вихід
    dp.register_callback_query_handler(exit_bot, lambda c: c.data and c.data == "exit")
    logger.info("✅ Зареєстровано exit_bot")
    
    logger.info("=== УСІ HANDLER'И START ЗАРЕЄСТРОВАНО ===")