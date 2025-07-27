import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiohttp import web
import asyncio
from handlers import register_all_handlers
from handlers.webhook import setup_webhooks
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
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

# Register all handlers
register_all_handlers(dp)

# Setup web server for webhooks
app = web.Application()
setup_webhooks(app, dp)

# Налагодження callback запитів
async def debug_callback(callback: types.CallbackQuery):
    """Налагодження callback запитів"""
    logger.info(f"Debug callback: {callback.data} from user {callback.from_user.id}")
    await callback.answer("Debug: отримано " + str(callback.data))

async def on_startup(dp):
    logger.info("Starting Kaminskyi AI Translator Bot...")
    # Додаємо налагодження
    # dp.register_callback_query_handler(debug_callback, lambda c: True, state="*")

async def on_shutdown(dp):
    logger.info("Shutting down Kaminskyi AI Translator Bot...")
    await dp.storage.close()
    await dp.storage.wait_closed()

if __name__ == '__main__':
    # Start both bot and web server
    loop = asyncio.get_event_loop()
    
    # Start web server
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', config.PORT)
    loop.run_until_complete(site.start())
    
    logger.info(f"Web server started on port {config.PORT}")
    
    # Start bot
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )