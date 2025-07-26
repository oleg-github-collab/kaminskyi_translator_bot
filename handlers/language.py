from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_language_keyboard
from states import TranslationStates
from locales.messages import MESSAGES
from utils.logger import log_user_action
import logging

logger = logging.getLogger(__name__)

async def choose_source_language(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ВИБОРУ МОВИ ОРИГІНАЛУ"""
    try:
        logger.info(f"=== ВИБІР МОВИ ОРИГІНАЛУ === User: {callback.from_user.id}, Data: {callback.data}")
        
        # ДЕТАЛЬНА ПЕРЕВІРКА ДАНИХ
        if not callback.data:
            logger.error(f"ПУСТІ ДАНІ від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Помилка даних", show_alert=True)
            return
            
        if not callback.data.startswith("lang_"):
            logger.error(f"НЕПРАВИЛЬНІ ДАНІ: {callback.data} від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Неправильні дані", show_alert=True)
            return
        
        await callback.answer()
        logger.info(f"Callback підтверджено для користувача {callback.from_user.id}")
        
        # Отримуємо вибрану мову
        language_code = callback.data.split("_")[1]  # lang_EN, lang_DE тощо
        logger.info(f"Вибрана мова оригіналу: {language_code} для користувача {callback.from_user.id}")
        
        # Зберігаємо мову оригіналу в стані
        await state.update_data(source_language=language_code)
        logger.info(f"Мова оригіналу збережена в стані для користувача {callback.from_user.id}")
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_target_language
        logger.info(f"Стан змінено для користувача {callback.from_user.id}")
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        logger.info(f"Мова користувача: {user_lang} для користувача {callback.from_user.id}")
        
        # Відправляємо повідомлення з вибором мови перекладу
        message_text = "🎯 <b>Крок 3/5:</b> Мова перекладу"
        keyboard = get_language_keyboard()
        await callback.message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
        logger.info(f"Повідомлення з мовами перекладу відправлено користувачу {callback.from_user.id}")
        
        log_user_action(callback.from_user.id, "selected_source_language", language_code)
        logger.info(f"=== ВИБІР МОВИ ОРИГІНАЛУ УСПІШНИЙ === User: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в choose_source_language для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Критична помилка вибору мови", show_alert=True)

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ВИБОРУ МОВИ ПЕРЕКЛАДУ"""
    try:
        logger.info(f"=== ВИБІР МОВИ ПЕРЕКЛАДУ === User: {callback.from_user.id}, Data: {callback.data}")
        
        # ДЕТАЛЬНА ПЕРЕВІРКА ДАНИХ
        if not callback.data:
            logger.error(f"ПУСТІ ДАНІ від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Помилка даних", show_alert=True)
            return
            
        if not callback.data.startswith("lang_"):
            logger.error(f"НЕПРАВИЛЬНІ ДАНІ: {callback.data} від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Неправильні дані", show_alert=True)
            return
        
        await callback.answer()
        logger.info(f"Callback підтверджено для користувача {callback.from_user.id}")
        
        # Отримуємо вибрану мову
        language_code = callback.data.split("_")[1]  # lang_EN, lang_DE тощо
        logger.info(f"Вибрана мова перекладу: {language_code} для користувача {callback.from_user.id}")
        
        # Зберігаємо мову перекладу в стані
        await state.update_data(target_language=language_code)
        logger.info(f"Мова перекладу збережена в стані для користувача {callback.from_user.id}")
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_file
        logger.info(f"Стан змінено для користувача {callback.from_user.id}")
        
        # Визначаємо мову користувача
        user_lang = callback.from_user.language_code or "en"
        user_lang = user_lang if user_lang in ["uk", "en", "de", "fr", "es"] else "en"
        logger.info(f"Мова користувача: {user_lang} для користувача {callback.from_user.id}")
        
        # Відправляємо повідомлення про надсилання файлу
        message_text = "🎯 <b>Крок 4/5:</b> Надішліть файл\n📄 Підтримуються: TXT, DOCX, PDF"
        await callback.message.answer(message_text, parse_mode="HTML")
        logger.info(f"Повідомлення про файл відправлено користувачу {callback.from_user.id}")
        
        log_user_action(callback.from_user.id, "selected_target_language", language_code)
        logger.info(f"=== ВИБІР МОВИ ПЕРЕКЛАДУ УСПІШНИЙ === User: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в choose_target_language для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Критична помилка вибору мови", show_alert=True)

def register_handlers_language(dp):
    """РЕЄСТРАЦІЯ ВСІХ HANDLER'ІВ ДЛЯ МОВ"""
    logger.info("=== РЕЄСТРАЦІЯ HANDLER'ІВ МОВ ===")
    
    # Для вибору мови оригіналу (БЕЗ СТАНУ - ТЕПЕР ПРАЦЮЄ)
    dp.register_callback_query_handler(choose_source_language, 
                                     lambda c: c.data and c.data.startswith("lang_"))
    logger.info("Зареєстровано choose_source_language")
    
    # Для вибору мови перекладу (БЕЗ СТАНУ - ТЕПЕР ПРАЦЮЄ)
    dp.register_callback_query_handler(choose_target_language, 
                                     lambda c: c.data and c.data.startswith("lang_"))
    logger.info("Зареєстровано choose_target_language")
    
    logger.info("=== УСІ HANDLER'И МОВ ЗАРЕЄСТРОВАНО ===")