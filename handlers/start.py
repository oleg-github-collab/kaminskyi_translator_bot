from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import get_model_keyboard, get_language_keyboard
from states import TranslationStates
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message, state: FSMContext):
    """СТАРТ БОТА"""
    try:
        logger.info(f"=== START БОТА === User ID: {message.from_user.id}")
        
        # ПОВНЕ СКИДАННЯ
        await state.finish()
        await state.reset_data()
        
        # Встановлюємо початковий стан
        await TranslationStates.choosing_model.set()
        
        # Відправляємо привітання
        welcome_message = """🎯 <b>Kaminskyi AI Translator</b>

Професійний переклад документів з використанням штучного інтелекту.

<b>Крок 1/5:</b> Оберіть модель перекладу:"""
        
        await message.answer(welcome_message, parse_mode="HTML")
        
        # Відправляємо клавіатуру моделей
        keyboard = get_model_keyboard("en")
        await message.answer("Виберіть модель:", reply_markup=keyboard)
        
        logger.info(f"=== START УСПІШНИЙ === User ID: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в cmd_start для користувача {message.from_user.id}: {str(e)}", exc_info=True)
        await message.answer("⚠️ Помилка. Спробуйте /start")

async def choose_model(callback: types.CallbackQuery, state: FSMContext):
    """ВИБІР МОДЕЛІ - ПРАЦЮЄ 100%"""
    try:
        logger.info(f"=== ВИБІР МОДЕЛІ === User ID: {callback.from_user.id}, Data: {callback.data}")
        
        # Перевірка даних
        if not callback.data:
            logger.error(f"ПУСТІ ДАНІ від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Помилка даних")
            return
            
        if not callback.data.startswith("model_"):
            logger.error(f"НЕПРАВИЛЬНІ ДАНІ: {callback.data} від користувача {callback.from_user.id}")
            await callback.answer("⚠️ Неправильні дані")
            return
        
        await callback.answer()
        logger.info(f"Callback підтверджено для користувача {callback.from_user.id}")
        
        # Отримуємо модель
        model = callback.data.split("_")[1]
        logger.info(f"Вибрана модель: {model} для користувача {callback.from_user.id}")
        
        await state.update_data(model=model)
        logger.info(f"Модель збережена в стані для користувача {callback.from_user.id}")
        
        # Переходимо до наступного стану
        await TranslationStates.next()  # waiting_for_source_language
        logger.info(f"Стан змінено для користувача {callback.from_user.id}")
        
        # Видаляємо попереднє повідомлення з кнопками
        try:
            await callback.message.delete()
        except:
            pass
        
        # Відправляємо вибір мови оригіналу
        model_name = "Kaminskyi Basic" if model == "basic" else "Kaminskyi Epic"
        await callback.message.answer(f"✅ Обрано модель: <b>{model_name}</b>\n\n📝 <b>Крок 2/5:</b> Оберіть мову оригіналу:", parse_mode="HTML")
        keyboard = get_language_keyboard()
        await callback.message.answer("Виберіть мову:", reply_markup=keyboard)
        
        logger.info(f"=== МОДЕЛЬ ВИБРАНА УСПІШНО === User ID: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"КРИТИЧНА ПОМИЛКА в choose_model для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Критична помилка вибору")

async def upload_another(callback: types.CallbackQuery, state: FSMContext):
    """ЗАВАНТАЖИТИ ІНШИЙ ФАЙЛ"""
    try:
        logger.info(f"=== ЗАВАНТАЖИТИ ІНШИЙ ФАЙЛ === User ID: {callback.from_user.id}")
        await callback.answer()
        
        # Повне скидання
        await state.finish()
        await state.reset_data()
        await TranslationStates.choosing_model.set()
        
        # Новий старт
        await callback.message.answer("🔄 <b>Новий переклад</b>\n\n<b>Крок 1/5:</b> Оберіть модель:", parse_mode="HTML")
        keyboard = get_model_keyboard("en")
        await callback.message.answer("Виберіть модель:", reply_markup=keyboard)
        
        logger.info(f"=== НОВИЙ ПЕРЕКЛАД РОЗПОЧАТО === User ID: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в upload_another для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка")

async def continue_translate(callback: types.CallbackQuery, state: FSMContext):
    """ПРОДОВЖЕННЯ ПЕРЕКЛАДУ"""
    try:
        logger.info(f"=== ПРОДОВЖЕННЯ ПЕРЕКЛАДУ === User ID: {callback.from_user.id}")
        await callback.answer()
        
        # Повне скидання
        await state.finish()
        await state.reset_data()
        await TranslationStates.choosing_model.set()
        
        # Новий старт
        await callback.message.answer("🎯 <b>Kaminskyi AI Translator</b>\n\n<b>Крок 1/5:</b> Оберіть модель:", parse_mode="HTML")
        keyboard = get_model_keyboard("en")
        await callback.message.answer("Виберіть модель:", reply_markup=keyboard)
        
        logger.info(f"=== ПРОДОВЖЕННЯ УСПІШНЕ === User ID: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в continue_translate для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка")

async def exit_bot(callback: types.CallbackQuery, state: FSMContext):
    """ВИХІД З БОТА"""
    try:
        logger.info(f"=== ВИХІД З БОТА === User ID: {callback.from_user.id}")
        await callback.answer()
        await state.finish()
        await state.reset_data()
        
        await callback.message.answer("👋 Дякуємо за використання Kaminskyi AI Translator!\n\nПовертайтесь знову: /start")
        
        logger.info(f"=== ВИХІД УСПІШНИЙ === User ID: {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"ПОМИЛКА в exit_bot для користувача {callback.from_user.id}: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Помилка")

def register_handlers_start(dp):
    """РЕЄСТРАЦІЯ HANDLER'ІВ"""
    logger.info("=== РЕЄСТРАЦІЯ HANDLER'ІВ СТАРТУ ===")
    
    # Старт в будь-якому стані
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    logger.info("Зареєстровано cmd_start")
    
    # Вибір моделі - З ПРАВИЛЬНИМИ ФІЛЬТРАМИ
    dp.register_callback_query_handler(
        choose_model,
        lambda c: c.data and c.data.startswith("model_"),
        state=TranslationStates.choosing_model
    )
    logger.info("Зареєстровано choose_model з фільтрами")
    
    # Завантажити інший файл
    dp.register_callback_query_handler(
        upload_another,
        lambda c: c.data and c.data == "upload_another",
        state="*"
    )
    logger.info("Зареєстровано upload_another")
    
    # Продовження
    dp.register_callback_query_handler(
        continue_translate,
        lambda c: c.data and c.data == "continue_translate",
        state="*"
    )
    logger.info("Зареєстровано continue_translate")
    
    # Вихід
    dp.register_callback_query_handler(
        exit_bot,
        lambda c: c.data and c.data == "exit",
        state="*"
    )
    logger.info("Зареєстровано exit_bot")
    
    logger.info("=== УСІ HANDLER'И СТАРТУ ЗАРЕЄСТРОВАНО ===")