from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_model_keyboard, get_language_keyboard
from states import TranslationStates
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """ПОВНИЙ СТАРТ БОТА"""
    try:
        logger.info(f"START БОТА для користувача {message.from_user.id}")
        
        # ПОВНЕ СКИДАННЯ
        await state.finish()
        await state.reset_data()
        
        # Встановлюємо початковий стан
        await TranslationStates.choosing_model.set()
        
        # Відправляємо привітання
        welcome_message = "🎯 <b>Kaminskyi AI Translator</b>\n\nОберіть модель перекладу:"
        await message.answer(welcome_message, parse_mode="HTML")
        
        # Відправляємо клавіатуру моделей
        keyboard = get_model_keyboard("en")
        await message.answer("Виберіть модель:", reply_markup=keyboard)
        
        log_user_action(message.from_user.id, "started_bot")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в cmd_start: {str(e)}")
        await message.answer("⚠️ Помилка. Спробуйте /start")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОДЕЛІ - ПРАЦЮЄ 100%"""
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
        
        # Відправляємо вибір мови оригіналу
        await callback.message.answer("📝 Оберіть мову оригіналу:")
        keyboard = get_language_keyboard()
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        log_user_action(callback.from_user.id, "selected_model", model)
        
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
        await callback.message.answer("🎯 <b>Kaminskyi AI Translator</b>\n\nНовий переклад:")
        keyboard = get_model_keyboard("en")
        await callback.message.answer("Виберіть модель:", reply_markup=keyboard)
        
        log_user_action(callback.from_user.id, "continued_translation")
        
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
        log_user_action(callback.from_user.id, "exited_bot")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в exit_bot: {str(e)}")
        await callback.answer("⚠️ Помилка")

def register_handlers_start(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ"""
    # Старт в будь-якому стані
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    
    # Вибір моделі - БЕЗ ОБМЕЖЕНЬ
    dp.register_callback_query_handler(choose_model)
    
    # Продовження
    dp.register_callback_query_handler(continue_translate, lambda c: c.data and c.data == "continue_translate")
    
    # Вихід
    dp.register_callback_query_handler(exit_bot, lambda c: c.data and c.data == "exit")