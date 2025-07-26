import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiohttp import web
import asyncio
import config

# Імпорт обробників у правильному порядку
from handlers import file, payment, language, start
from handlers.webhook import setup_webhooks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create directories
os.makedirs(config.TEMP_DIR, exist_ok=True)
os.makedirs(config.LOGS_DIR, exist_ok=True)

# Initialize bot
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# === КРИТИЧНО ВАЖЛИВИЙ ПОРЯДОК РЕЄСТРАЦІЇ ОБРОБНИКІВ ===
# Від найбільш специфічних до найменш специфічних

# 1. Реєстрація обробників файлів (найбільш специфічні - тільки для конкретного стану)
file.register_handlers_file(dp)
logger.info("✅ Зареєстровано обробники файлів")

# 2. Реєстрація обробників оплати
payment.register_handlers_payment(dp)
logger.info("✅ Зареєстровано обробники оплати")

# 3. Реєстрація обробників мов (специфічні callback_data + стан)
language.register_handlers_language(dp)
logger.info("✅ Зареєстровано обробники мов")

# 4. Реєстрація обробників старту (включає загальні обробники)
# ВАЖЛИВО: цей модуль має бути ОСТАННІМ
start.register_handlers_start(dp)
logger.info("✅ Зареєстровано обробники старту")

# === DEBUG MODE (розкоментуйте для налагодження) ===
# async def debug_callback(callback: types.CallbackQuery):
#     """Налагодження callback запитів"""
#     logger.info(f"🔍 Debug callback: data='{callback.data}' from user {callback.from_user.id}")
#     current_state = await dp.current_state(user=callback.from_user.id).get_state()
#     logger.info(f"🔍 Current state: {current_state}")
#     await callback.answer(f"Debug: {callback.data}")

# # Реєстрація debug обробника (має бути ОСТАННІМ)
# dp.register_callback_query_handler(debug_callback, lambda c: True, state="*")
# logger.info("🔍 Debug mode enabled")

# Setup web server for webhooks
app = web.Application()
setup_webhooks(app)

async def on_startup(dp):
    """Дії при запуску бота"""
    logger.info("🚀 Starting Kaminskyi AI Translator Bot...")
    
    # Отримання інформації про бота
    bot_info = await bot.get_me()
    logger.info(f"🤖 Bot: @{bot_info.username} (ID: {bot_info.id})")
    
    # Видалення webhook (для polling mode)
    await bot.delete_webhook()
    logger.info("📡 Webhook deleted, using long polling")
    
    # Якщо потрібен webhook mode, розкоментуйте:
    # await bot.set_webhook(config.WEBHOOK_URL)
    # logger.info(f"📡 Webhook set to: {config.WEBHOOK_URL}")

async def on_shutdown(dp):
    """Дії при зупинці бота"""
    logger.info("🛑 Shutting down Kaminskyi AI Translator Bot...")
    
    # Закриття сховища
    await dp.storage.close()
    await dp.storage.wait_closed()
    
    # Видалення webhook
    await bot.delete_webhook()
    
    # Закриття сесії бота
    await bot.session.close()
    
    logger.info("👋 Bot stopped successfully")

if __name__ == '__main__':
    # Перевірка конфігурації
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in config!")
        exit(1)
    
    # Використовуємо різні режими залежно від налаштувань
    if hasattr(config, 'USE_WEBHOOK') and config.USE_WEBHOOK:
        # === WEBHOOK MODE ===
        logger.info("🌐 Starting in WEBHOOK mode")
        
        # Start web server
        loop = asyncio.get_event_loop()
        
        runner = web.AppRunner(app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, '0.0.0.0', config.PORT)
        loop.run_until_complete(site.start())
        
        logger.info(f"🌐 Web server started on port {config.PORT}")
        
        # Start bot with webhook
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host='0.0.0.0',
            port=config.PORT
        )
    else:
        # === POLLING MODE (рекомендовано для розробки) ===
        logger.info("🔄 Starting in POLLING mode")
        
        executor.start_polling(
            dp,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            allowed_updates=['message', 'callback_query']
        )