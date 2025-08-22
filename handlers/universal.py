from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
from utils.simple_debug import debug_callback, log_action
from utils.flow_manager import flow_manager, safe_callback_handler
from utils.language_system import (
    create_language_menu_keyboard, create_popular_languages_keyboard,
    create_all_languages_keyboard, create_regional_keyboard,
    LANGUAGE_REGIONS
)
import logging

logger = logging.getLogger(__name__)

@debug_callback
async def universal_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    """УНІВЕРСАЛЬНИЙ ОБРОБНИК ВСІХ CALLBACK'ІВ - FALLBACK СИСТЕМА"""
    user_id = callback.from_user.id
    callback_data = callback.data
    
    try:
        logger.info(f"🔧 УНІВЕРСАЛЬНИЙ ОБРОБНИК: {callback_data} для користувача {user_id}")
        
        # Отримуємо поточний стан
        current_state = await state.get_state()
        user_data = await state.get_data()
        
        # Логуємо детальну інформацію
        log_action("universal_callback_received", user_id, f"data: {callback_data}, state: {current_state}")
        
        # === ОБРОБКА CALLBACK'ІВ ПО ТИПАХ ===
        
        # 1. ВИБІР МОДЕЛІ
        if callback_data and callback_data.startswith("model_"):
            return await handle_model_selection(callback, state)
        
        # 2. ВИБІР МОВИ - делегуємо до правильних обробників
        elif callback_data and callback_data.startswith("lang_page_"):
            # Пагінація мов
            from handlers.language import handle_language_pagination
            return await handle_language_pagination(callback, state)
        elif callback_data == "page_info":
            # Інформація про сторінку
            from handlers.language import handle_page_info
            await handle_page_info(callback, state)
            return True
        elif callback_data and callback_data.startswith("lang_"):
            # Вибір мови
            current_state = await state.get_state()
            if "waiting_for_source_language" in str(current_state):
                from handlers.language import choose_source_language
                await choose_source_language(callback, state)
                return True
            elif "waiting_for_target_language" in str(current_state):
                from handlers.language import choose_target_language  
                await choose_target_language(callback, state)
                return True
            else:
                return await handle_language_selection(callback, state)
        
        # 3. ПЛАТІЖНІ CALLBACK'И
        elif callback_data in ["process_payment", "payment_done", "upload_another", "payment_help"]:
            return await handle_payment_callbacks(callback, state)
        
        # 4. МЕНЮ МОВ
        elif callback_data and callback_data.startswith("lang_menu_"):
            return await handle_language_menu(callback, state)
        
        # 5. НАВІГАЦІЙНІ CALLBACK'И
        elif callback_data in ["continue_translate", "exit", "lang_menu_back"]:
            return await handle_navigation_callbacks(callback, state)
        
        # 6. НЕВІДОМІ CALLBACK'И
        else:
            return await handle_unknown_callback(callback, state)
            
    except Exception as e:
        logger.error(f"❌ КРИТИЧНА ПОМИЛКА в universal_callback_handler: {str(e)}")
        await callback.answer("⚠️ Сталася помилка")
        
        # Спроба відновлення
        recovery_result = await flow_manager.handle_error_recovery(user_id, state, str(e))
        
        if recovery_result == "restarted":
            await callback.message.answer(
                "🔄 Сталася помилка, перезапускаємо процес.\n"
                "Оберіть модель для перекладу:"
            )
            
            # Показуємо кнопки моделей
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                types.InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
                types.InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
            )
            await callback.message.answer("Виберіть модель:", reply_markup=keyboard)

async def handle_model_selection(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ВИБОРУ МОДЕЛІ"""
    user_id = callback.from_user.id
    
    try:
        logger.info(f"🎯 ОБРОБКА ВИБОРУ МОДЕЛІ: {callback.data} для користувача {user_id}")
        
        # Перевірка формату даних
        if not callback.data.startswith("model_"):
            await callback.answer("⚠️ Неправильний формат")
            return False
        
        # Отримуємо модель
        model_parts = callback.data.split("_")
        if len(model_parts) != 2:
            await callback.answer("⚠️ Неправильний формат моделі")
            return False
        
        model = model_parts[1]
        if model not in ["basic", "epic"]:
            await callback.answer("⚠️ Невідома модель")
            return False
        
        await callback.answer()
        
        # Зберігаємо модель
        await state.update_data(model=model)
        
        # Перехід до наступного стану
        success = await flow_manager.safe_state_transition(
            user_id=user_id,
            state=state,
            target_state="waiting_for_source_language",
            trigger=f"model_selected_{model}"
        )
        
        if not success:
            await callback.message.answer("❌ Помилка переходу стану")
            return False
        
        # Відправляємо повідомлення про вибір мови
        model_name = "Kaminskyi Basic" if model == "basic" else "Kaminskyi Epic"
        await callback.message.answer(f"✅ Обрано модель: {model_name}")
        
        # Показуємо кількість доступних мов залежно від моделі
        from handlers.language import get_supported_languages
        supported_langs = get_supported_languages(model)
        lang_count = len(supported_langs)
        
        await callback.message.answer(
            f"<b>Крок 2/5:</b> Оберіть мову оригіналу:\n"
            f"🌍 Доступно {lang_count} мов",
            parse_mode="HTML"
        )
        
        # Показуємо клавіатуру мов для вибраної моделі  
        from keyboards.inline import get_language_keyboard
        keyboard = get_language_keyboard(model, page=0)
        await callback.message.answer("Оберіть мову оригіналу:", reply_markup=keyboard)
        
        logger.info(f"✅ МОДЕЛЬ {model} успішно обрана для користувача {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_model_selection: {str(e)}")
        return False

async def handle_language_selection(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ВИБОРУ МОВИ"""
    user_id = callback.from_user.id
    current_state = await state.get_state()
    
    try:
        logger.info(f"🌐 ОБРОБКА ВИБОРУ МОВИ: {callback.data} для користувача {user_id}, стан: {current_state}")
        
        # Перевірка формату
        if not callback.data.startswith("lang_"):
            await callback.answer("⚠️ Неправильний формат мови")
            return False
        
        language_code = callback.data.split("_")[1]
        await callback.answer()
        
        # Валідація мови - використовуємо правильні функції
        from handlers.language import get_language_name, get_supported_languages
        
        # Отримуємо дані користувача для валідації
        user_data = await state.get_data()
        model = user_data.get('model', 'basic')
        supported_languages = get_supported_languages(model)
        
        if language_code not in supported_languages:
            await callback.answer("⚠️ Мова не підтримується цією моделлю")
            return False
        
        lang_name = get_language_name(language_code)
        
        # ЛОГІКА ЗАЛЕЖНО ВІД ПОТОЧНОГО СТАНУ
        if current_state == "TranslationStates:waiting_for_source_language":
            # Вибір мови оригіналу
            await state.update_data(source_language=language_code)
            
            await flow_manager.safe_state_transition(
                user_id=user_id,
                state=state,
                target_state="waiting_for_target_language",
                trigger=f"source_lang_selected_{language_code}"
            )
            
            await callback.message.answer(f"✅ Мова оригіналу: {lang_name}")
            
            # Показуємо кількість доступних мов залежно від моделі
            lang_count = len(supported_languages)
            await callback.message.answer(
                f"<b>Крок 3/5:</b> Оберіть мову перекладу:\n"
                f"🌍 Доступно {lang_count} мов",
                parse_mode="HTML"
            )
            
            # Показуємо клавіатуру мов для вибраної моделі
            from keyboards.inline import get_language_keyboard
            keyboard = get_language_keyboard(model, page=0)
            await callback.message.answer("Оберіть мову перекладу:", reply_markup=keyboard)
            
        elif current_state == "TranslationStates:waiting_for_target_language":
            # Вибір мови перекладу
            user_data = await state.get_data()
            source_lang = user_data.get('source_language')
            
            # Перевірка на однакові мови
            if source_lang == language_code:
                await callback.message.answer("⚠️ Мови оригіналу та перекладу не можуть бути однаковими!")
                return False
            
            await state.update_data(target_language=language_code)
            
            await flow_manager.safe_state_transition(
                user_id=user_id,
                state=state,
                target_state="waiting_for_file",
                trigger=f"target_lang_selected_{language_code}"
            )
            
            await callback.message.answer(f"✅ Мова перекладу: {lang_name}")
            await callback.message.answer("<b>Крок 4/5:</b> Надішліть файл для перекладу", parse_mode="HTML")
            await callback.message.answer("📄 Підтримуються формати: TXT, DOCX, PDF")
            
        else:
            await callback.message.answer("⚠️ Неправильний стан для вибору мови")
            return False
        
        logger.info(f"✅ МОВА {language_code} успішно обрана для користувача {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_language_selection: {str(e)}")
        return False

async def handle_payment_callbacks(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА ПЛАТІЖНИХ CALLBACK'ІВ"""
    user_id = callback.from_user.id
    
    try:
        logger.info(f"💳 ПЛАТІЖНИЙ CALLBACK: {callback.data} для користувача {user_id}")
        
        # Перенаправляємо до оригінальних handler'ів з payment.py
        from handlers.payment import (
            process_payment, payment_done, upload_another, payment_help
        )
        
        if callback.data == "process_payment":
            return await safe_callback_handler(callback, state, process_payment, "process_payment")
        elif callback.data == "payment_done":
            return await safe_callback_handler(callback, state, payment_done, "payment_done")
        elif callback.data == "upload_another":
            return await safe_callback_handler(callback, state, upload_another, "upload_another")
        elif callback.data == "payment_help":
            return await safe_callback_handler(callback, state, payment_help, "payment_help")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_payment_callbacks: {str(e)}")
        return False

async def handle_language_menu(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА МЕНЮ МОВ"""
    user_id = callback.from_user.id
    
    try:
        logger.info(f"🌍 МЕНЮ МОВ: {callback.data} для користувача {user_id}")
        
        menu_type = callback.data.replace("lang_menu_", "")
        await callback.answer()
        
        if menu_type == "popular":
            keyboard = create_popular_languages_keyboard()
            await callback.message.edit_text(
                "🔥 **Популярні мови:**\nОберіть мову:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        elif menu_type == "all":
            keyboard = create_all_languages_keyboard()
            await callback.message.edit_text(
                "🌍 **Всі доступні мови:**\nОберіть мову:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        elif menu_type == "european":
            keyboard = create_regional_keyboard("European")
            await callback.message.edit_text(
                "🇪🇺 **Європейські мови:**\nОберіть мову:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        elif menu_type == "asian":
            keyboard = create_regional_keyboard("Asian")
            await callback.message.edit_text(
                "🌏 **Азійські мови:**\nОберіть мову:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        elif menu_type == "african":
            keyboard = create_regional_keyboard("African")
            await callback.message.edit_text(
                "🌍 **Африканські мови:**\nОберіть мову:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
        elif menu_type == "americas":
            keyboard = create_regional_keyboard("Americas")
            await callback.message.edit_text(
                "🌎 **Мови Америки:**\nОберіть мову:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await callback.message.answer("⚠️ Невідомий тип меню")
            return False
        
        # Додаємо кнопку "Назад" до всіх меню
        back_button = types.InlineKeyboardButton("🔙 Назад до категорій", callback_data="lang_menu_back")
        keyboard.add(back_button)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_language_menu: {str(e)}")
        return False

async def handle_navigation_callbacks(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА НАВІГАЦІЙНИХ CALLBACK'ІВ"""
    user_id = callback.from_user.id
    
    try:
        logger.info(f"🧭 НАВІГАЦІЙНИЙ CALLBACK: {callback.data} для користувача {user_id}")
        
        if callback.data == "continue_translate":
            # Повний перезапуск
            await flow_manager.reset_user_completely(user_id, state)
            await flow_manager.safe_state_transition(user_id, state, "choosing_model", "continue_translate")
            
            await callback.answer()
            await callback.message.answer(
                "🎯 <b>Новий переклад</b>\n\n"
                "<b>Крок 1/5:</b> Оберіть модель:",
                parse_mode="HTML"
            )
            
            # Кнопки моделей
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                types.InlineKeyboardButton("⚡ Kaminskyi Basic", callback_data="model_basic"),
                types.InlineKeyboardButton("🎯 Kaminskyi Epic", callback_data="model_epic")
            )
            await callback.message.answer("Виберіть модель:", reply_markup=keyboard)
            
        elif callback.data == "exit":
            await callback.answer()
            await flow_manager.reset_user_completely(user_id, state)
            await callback.message.answer("👋 Дякуємо за використання! Для нового перекладу натисніть /start")
            
        elif callback.data == "lang_menu_back":
            # Повернення до головного меню мов
            await callback.answer()
            keyboard = create_language_menu_keyboard()
            current_state = await state.get_state()
            
            if "waiting_for_source_language" in str(current_state):
                text = "🌍 **Оберіть мову оригіналу:**\nВиберіть категорію:"
            else:
                text = "🌍 **Оберіть мову перекладу:**\nВиберіть категорію:"
            
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_navigation_callbacks: {str(e)}")
        return False

async def handle_unknown_callback(callback: types.CallbackQuery, state: FSMContext):
    """ОБРОБКА НЕВІДОМИХ CALLBACK'ІВ"""
    user_id = callback.from_user.id
    
    try:
        logger.warning(f"❓ НЕВІДОМИЙ CALLBACK: {callback.data} для користувача {user_id}")
        
        await callback.answer("⚠️ Невідома команда")
        
        # Показуємо поточний прогрес
        await flow_manager.send_progress_message(user_id, state, callback.message)
        
        # Пропонуємо варіанти
        await callback.message.answer(
            "❓ Незрозуміла команда. Виберіть дію:",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🔄 Почати заново", callback_data="continue_translate"),
                types.InlineKeyboardButton("📊 Мій прогрес", callback_data="show_progress")
            )
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА в handle_unknown_callback: {str(e)}")
        return False

def register_handlers_universal(dp):
    """РЕЄСТРАЦІЯ УНІВЕРСАЛЬНОГО HANDLER'А - ОСТАННІЙ В ЧЕРЗІ"""
    logger.info("=== РЕЄСТРАЦІЯ УНІВЕРСАЛЬНОГО HANDLER'А ===")
    
    # Універсальний handler для всіх callback'ів (найнижчий пріоритет)
    dp.register_callback_query_handler(universal_callback_handler, lambda c: True, state="*")
    logger.info("✅ Зареєстровано universal_callback_handler")
    
    logger.info("=== УНІВЕРСАЛЬНИЙ HANDLER ЗАРЕЄСТРОВАНО ===")