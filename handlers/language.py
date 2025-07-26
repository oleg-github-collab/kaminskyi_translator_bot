from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_language_keyboard
from states import TranslationStates
import logging

# Налаштування логування
logger = logging.getLogger(__name__)

async def choose_source_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ОРИГІНАЛУ"""
    try:
        logger.info(f"=== ВИБІР МОВИ ОРИГІНАЛУ === User ID: {callback.from_user.id}, Data: {callback.data}")
        
        # Перевірка даних
        if not callback.data:
            logger.error(f"ПУСТІ ДАНІ від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Помилка даних")
            return
            
        if not callback.data.startswith("lang_"):
            logger.error(f"НЕПРАВИЛЬНІ ДАНІ: {callback.data} від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        logger.info(f"Callback підтверджено для користувача {callback.from_user.id}")
        
        # Отримуємо мову
        language_code = callback.data.split("_")[1]
        logger.info(f"Вибрана мова оригіналу: {language_code} для користувача {callback.from_user.id}")
        
        await state.update_data(source_language=language_code)
        logger.info(f"Мова оригіналу збережена в стані для користувача {callback.from_user.id}")
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_target_language
        logger.info(f"Стан змінено для користувача {callback.from_user.id}")
        
        # Видаляємо попереднє повідомлення з кнопками
        try:
            await callback.message.delete()
        except:
            pass
        
        # Відправляємо вибір мови перекладу
        await callback.message.answer("🌍 <b>Крок 3/5:</b> Оберіть мову перекладу:", parse_mode="HTML")
        keyboard = get_language_keyboard()
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        logger.info(f"=== МОВА ОРИГІНАЛУ ВИБРАНА УСПІШНО === User ID: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в choose_source_language для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Критична помилка")

async def choose_target_language(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОВИ ПЕРЕКЛАДУ"""
    try:
        logger.info(f"=== ВИБІР МОВИ ПЕРЕКЛАДУ === User ID: {callback.from_user.id}, Data: {callback.data}")
        
        # Перевірка даних
        if not callback.data:
            logger.error(f"ПУСТІ ДАНІ від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Помилка даних")
            return
            
        if not callback.data.startswith("lang_"):
            logger.error(f"НЕПРАВИЛЬНІ ДАНІ: {callback.data} від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        logger.info(f"Callback підтверджено для користувача {callback.from_user.id}")
        
        # Отримуємо мову
        language_code = callback.data.split("_")[1]
        logger.info(f"Вибрана мова перекладу: {language_code} для користувача {callback.from_user.id}")
        
        # Перевірка, що мови різні
        user_data = await state.get_data()
        source_lang = user_data.get('source_language')
        
        if source_lang == language_code:
            await callback.answer("⚠️ Оберіть іншу мову для перекладу!", show_alert=True)
            return
        
        await state.update_data(target_language=language_code)
        logger.info(f"Мова перекладу збережена в стані для користувача {callback.from_user.id}")
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_file
        logger.info(f"Стан змінено для користувача {callback.from_user.id}")
        
        # Видаляємо попереднє повідомлення з кнопками
        try:
            await callback.message.delete()
        except:
            pass
        
        # Відправляємо запит на файл
        await callback.message.answer("📥 <b>Крок 4/5:</b> Надішліть файл для перекладу", parse_mode="HTML")
        await callback.message.answer("📄 Підтримувані формати: TXT, DOCX, PDF\n📏 Максимальний розмір: 20 МБ", parse_mode="HTML")
        
        logger.info(f"=== МОВА ПЕРЕКЛАДУ ВИБРАНА УСПІШНО === User ID: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в choose_target_language для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Критична помилка")

def register_handlers_language(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ МОВ"""
    logger.info("=== РЕЄСТРАЦІЯ HANDLER'ІВ МОВ ===")
    
    # Вибір мови оригіналу - З ПРАВИЛЬНИМИ ФІЛЬТРАМИ
    dp.register_callback_query_handler(
        choose_source_language,
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_source_language
    )
    logger.info("Зареєстровано choose_source_language з фільтрами")
    
    # Вибір мови перекладу - З ПРАВИЛЬНИМИ ФІЛЬТРАМИ
    dp.register_callback_query_handler(
        choose_target_language,
        lambda c: c.data and c.data.startswith("lang_"),
        state=TranslationStates.waiting_for_target_language
    )
    logger.info("Зареєстровано choose_target_language з фільтрами")
    
    logger.info("=== УСІ HANDLER'И МОВ ЗАРЕЄСТРОВАНО ===")