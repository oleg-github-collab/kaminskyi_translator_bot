import logging
import os
from datetime import datetime
from config import LOGS_DIR

# Create logs directory
os.makedirs(LOGS_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOGS_DIR}/bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

def get_logger(name: str):
    return logging.getLogger(name)

def log_user_action(user_id: int, action: str, details: str = ""):
    logger = get_logger("user_actions")
    logger.info(f"User {user_id}: {action} - {details}")

def log_error(error: Exception, context: str = ""):
    logger = get_logger("errors")
    logger.error(f"{context} - {str(error)}", exc_info=True)

def log_translation(user_id: int, model: str, chars: int, price: float):
    logger = get_logger("translations")
    logger.info(f"User {user_id}: {model} translation - {chars} chars, {price}€")