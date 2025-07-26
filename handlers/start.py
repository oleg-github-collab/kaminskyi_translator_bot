from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_model_keyboard, get_continue_keyboard, get_language_keyboard
from states import TranslationStates
from locales.messages import MESSAGES
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """ПОЧАТОК БОТА - завжди з чистого листа"""
    try:
        logger.info(f"=== START БОТА === User: {message.from_user.id}")
        
        # ЗАВЖДИ скидаємо весь стан
        await state.finish()
        await state.reset_data()
        
        # Визначаємо мову користувача
        user_lang = message.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Відправляємо привітання
        welcome_message = "🎯 <b>Kaminskyi AI Translator</b>\n\n"
        welcome_message += "⚡ Швидкий та якісний переклад файлів\n"
        welcome_message += "📄 Підтримка: TXT, DOCX, PDF\n"
        welcome_message += "💰 Вигідні ціни\n\n"
        welcome_message += "<b>Оберіть модель перекладу:</b>"
        
        await message.answer(welcome_message, parse_mode="HTML")
        
        # Встановлюємо стан вибору моделі
        await TranslationStates.choosing_model.set()
        
        # Відправляємо клавіатуру вибору моделі
        keyboard = get_model_keyboard(user_lang)
        step_message = "🎯 <b>Крок 1/5:</b> Оберіть модель"
        await message.answer(step_message, reply_markup=keyboard, parse_mode="HTML")
        
        log_user_action(message.from_user.id, "started_bot", f"language: {user_lang}")
        logger.info(f"=== START УСПІШНИЙ === User: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в cmd_start для користувача {message.from_user.id}: {str(e)}", exc_info=True)
        await message.answer("⚠️ <b>Технічні проблеми</b>\nСпробуйте ще раз команду /start", parse_mode="HTML")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ВИБОРУ МОДЕЛІ ПЕРЕКЛАДУ"""
    try:
        logger.info(f"=== ВИБІР МОДЕЛІ === User: {callback.from_user.id}, Data: {callback.data}")
        
        # ДЕТАЛЬНА ПЕРЕВІРКА ДАНИХ
        if not callback.data:
            logger.error(f"ПУСТІ ДАНІ від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Помилка даних", show_alert=True)
            return
            
        if not callback.data.startswith("model_"):
            logger.error(f"НЕПРАВИЛЬНІ ДАНІ: {callback.data} від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Неправильні дані", show_alert=True)
            return
        
        await callback.answer()
        logger.info(f"Callback підтверджено для користувача {callback.from_user.id}")
        
        # Отримуємо вибрану модель
        model = callback.data.split("_")[1]  # model_basic або model_epic
        logger.info(f"Вибрана модель: {model} для користувача {callback.from_user.id}")
        
        # Зберігаємо модель в стані
        await state.update_data(model=model)
        logger.info(f"Модель збережена в стані для користувача {callback.from_user.id}")
        
        # Переходимо до наступного стану
        current_state = await state.get_state()
        logger.info(f"Поточний стан перед переходом: {current_state} для користувача {callback.from_user.id}")
        
        await TranslationStates.next()  # waiting_for_source_language
        logger.info(f"Стан змінено для користувача {callback.from_user.id}")
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        logger.info(f"Мова користувача: {user_lang} для користувача {callback.from_user.id}")
        
        # Відправляємо повідомлення з вибором мови оригіналу
        message_text = "🎯 <b>Крок 2/5:</b> Мова оригіналу"
        keyboard = get_language_keyboard()
        await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
        logger.info(f"Повідомлення з мовами відправлено користувачу {callback.from_user.id}")
        
        log_user_action(callback.from_user.id, "selected_model", model)
        logger.info(f"=== ВИБІР МОДЕЛІ УСПІШНИЙ === User: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в choose_model для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Критична помилка вибору моделі", show_alert=True)

async def continue_translate(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ПРОДОВЖЕННЯ ПЕРЕКЛАДУ"""
    try:
        logger.info(f"=== ПРОДОВЖЕННЯ ПЕРЕКЛАДУ === User: {callback.from_user.id}")
        await callback.answer()
        
        # РАДИКАЛЬНЕ СКИДАННЯ
        await state.finish()
        await state.reset_data()
        await TranslationStates.choosing_model.set()
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        
        # Відправляємо привітання
        welcome_message = "🎯 <b>Kaminskyi AI Translator</b>\n\n<b>Новий переклад:</b>"
        await callback.message.answer(welcome_message, parse_mode="HTML")
        
        # Відправляємо клавіатуру вибору моделі
        keyboard = get_model_keyboard(user_lang)
        step_message = "🎯 <b>Крок 1/5:</b> Оберіть модель"
        await callback.message.answer(step_message, reply_markup=keyboard, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "continued_translation")
        logger.info(f"=== ПРОДОВЖЕННЯ УСПІШНЕ === User: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в continue_translate для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка", show_alert=True)

async def exit_bot(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ВИХОДУ З БОТА"""
    try:
        logger.info(f"=== ВИХІД З БОТА === User: {callback.from_user.id}")
        await callback.answer()
        
        # Повне скидання
        await state.finish()
        await state.reset_data()
        
        # Відправляємо повідомлення про вихід
        exit_message = "👋 Дякуємо за використання Kaminskyi AI Translator!\n\nПовертайтесь знову: /start"
        await callback.message.answer(exit_message, parse_mode="HTML")
        
        log_user_action(callback.from_user.id, "exited_bot")
        logger.info(f"=== ВИХІД УСПІШНИЙ === User: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в exit_bot для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка", show_alert=True)

def register_handlers_start(dp):
    """РЕЄСТРАЦІЯ ВСІХ HANDLER'ІВ ДЛЯ СТАРТУ"""
    logger.info("=== РЕЄСТРАЦІЯ HANDLER'ІВ СТАРТУ ===")
    
    # Обробка команди /start в будь-якому стані
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    logger.info("Зареєстровано cmd_start")
    
    # Обробка вибору моделі (ТЕПЕР ПРАВИЛЬНО)
    dp.register_callback_query_handler(choose_model, 
                                     lambda c: c.data and c.data.startswith("model_"))
    logger.info("Зареєстровано choose_model")
    
    # Обробка продовження перекладу
    dp.register_callback_query_handler(continue_translate, 
                                     lambda c: c.data and c.data == "continue_translate")
    logger.info("Зареєстровано continue_translate")
    
    # Обробка виходу
    dp.register_callback_query_handler(exit_bot, 
                                     lambda c: c.data and c.data == "exit")
    logger.info("Зареєстровано exit_bot")
    
    logger.info("=== УСІ HANDLER'И СТАРТУ ЗАРЕЄСТРОВАНО ===")