from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_model_keyboard, get_continue_keyboard
from states import TranslationStates
from locales.messages import MESSAGES
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """РАДИКАЛЬНО ПОКРАЩЕНИЙ старт - завжди з чистого листа"""
    try:
        logger.info(f"=== НОВИЙ СТАРТ БОТА === User: {message.from_user.id}")
        
        # ЗАВЖДИ скидаємо весь стан
        current_state = await state.get_state()
        if current_state:
            logger.info(f"Скидаємо попередній стан: {current_state} для користувача {message.from_user.id}")
            await state.finish()
        
        # Очищуємо всі попередні дані
        await state.reset_data()
        
        # Визначаємо мову користувача
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Відправляємо привітання з гарним дизайном
        welcome_message = "🎯 <b>Kaminskyi AI Translator</b>\n\n"
        welcome_message += "⚡ Швидкий та якісний переклад файлів\n"
        welcome_message += "📄 Підтримка: TXT, DOCX, PDF\n"
        welcome_message += "💰 Вигідні ціни\n\n"
        welcome_message += "Оберіть модель перекладу:"
        
        await message.answer(welcome_message, parse_mode="HTML")
        
        # Встановлюємо стан вибору моделі
        await TranslationStates.choosing_model.set()
        
        # Відправляємо клавіатуру вибору моделі
        keyboard = get_model_keyboard(user_lang)
        step_message = "🎯 <b>Крок 1/5:</b> Оберіть модель"
        await message.answer(step_message, reply_markup=keyboard, parse_mode="HTML")
        
        log_user_action(message.from_user.id, "started_bot", f"language: {user_lang}")
        logger.info(f"=== СТАРТ УСПІШНО ЗАВЕРШЕНО === User: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в cmd_start для користувача {message.from_user.id}: {str(e)}", exc_info=True)
        await message.answer("⚠️ <b>Технічні проблеми</b>\nСпробуйте ще раз команду /start", parse_mode="HTML")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    """Обробка вибору моделі перекладу"""
    try:
        logger.info(f"Вибір моделі для користувача {callback.from_user.id}")
        
        # Перевірка даних
        if not callback.data or not callback.data.startswith("model_"):
            await callback.answer("⚠️ Невірні дані", show_alert=True)
            return
            
        await callback.answer()
        
        # Отримуємо вибрану модель
        model = callback.data.split("_")[1]  # model_basic або model_epic
        
        # Зберігаємо модель в стані
        await state.update_data(model=model)
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_source_language
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Відправляємо повідомлення з вибором мови оригіналу
        message_text = "🎯 <b>Крок 2/5:</b> Мова оригіналу"
        keyboard = get_language_keyboard()
        await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "selected_model", model)
        logger.info(f"Модель {model} вибрана для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в choose_model для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка вибору моделі", show_alert=True)

async def continue_translate(callback: types.CallbackQuery, state: FSMContext):
    """Обробка продовження перекладу"""
    try:
        logger.info(f"Продовження перекладу для користувача {callback.from_user.id}")
        await callback.answer()
        
        # РАДИКАЛЬНЕ СКИДАННЯ - все з початку
        await state.finish()
        await state.reset_data()
        await TranslationStates.choosing_model.set()
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Відправляємо привітання
        welcome_message = "🎯 <b>Kaminskyi AI Translator</b>\n\nНовий переклад:"
        await callback.message.answer(welcome_message, parse_mode="HTML")
        
        # Відправляємо клавіатуру вибору моделі
        keyboard = get_model_keyboard(user_lang)
        step_message = "🎯 <b>Крок 1/5:</b> Оберіть модель"
        await callback.message.answer(step_message, reply_markup=keyboard, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "continued_translation")
        logger.info(f"Продовження перекладу успішне для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в continue_translate для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка", show_alert=True)

async def exit_bot(callback: types.CallbackQuery, state: FSMContext):
    """Обробка виходу з бота"""
    try:
        logger.info(f"Вихід з бота для користувача {callback.from_user.id}")
        await callback.answer()
        
        # Повне скидання
        await state.finish()
        await state.reset_data()
        
        # Відправляємо повідомлення про вихід
        exit_message = "👋 Дякуємо за використання Kaminskyi AI Translator!\n\nПовертайтесь знову /start"
        await callback.message.answer(exit_message, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "exited_bot")
        logger.info(f"Вихід успішний для користувача {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в exit_bot для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка", show_alert=True)

def register_handlers_start(dp):
    """Реєстрація handler'ів для старту"""
    # Обробка команди /start в будь-якому стані
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    
    # Обробка вибору моделі
    dp.register_callback_query_handler(choose_model, 
                                     lambda c: c.data and c.data.startswith("model_"), 
                                     state=TranslationStates.choosing_model)
    
    # Обробка продовження перекладу
    dp.register_callback_query_handler(continue_translate, 
                                     lambda c: c.data and c.data == "continue_translate")
    
    # Обробка виходу
    dp.register_callback_query_handler(exit_bot, 
                                     lambda c: c.data and c.data == "exit")