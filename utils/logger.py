import logging
import os
from datetime import datetime
from config import LOGS_DIR

# Створення директорії для логів
os.makedirs(LOGS_DIR, exist_ok=True)

# Налаштування логування з максимальним деталізацією
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOGS_DIR}/bot_detailed_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.FileHandler(f'{LOGS_DIR}/bot_errors_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
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

def log_payment(user_id: int, amount: float, status: str):
    logger = get_logger("payments")
    logger.info(f"User {user_id}: Payment {status} - {amount}€")

def log_state_change(user_id: int, old_state: str, new_state: str):
    logger = get_logger("state_changes")
    logger.info(f"User {user_id}: State changed from {old_state} to {new_state}")

def log_file_operation(user_id: int, operation: str, file_path: str, details: str = ""):
    logger = get_logger("file_operations")
    logger.info(f"User {user_id}: {operation} - {file_path} - {details}")