import logging
import os
from datetime import datetime
from functools import wraps

# Створюємо директорії
os.makedirs('logs', exist_ok=True)

# Налаштовуємо простий надійний логгер
logger = logging.getLogger('bot_debug')
logger.setLevel(logging.DEBUG)

# File handler
if not logger.handlers:  # Уникаємо дублювання
    file_handler = logging.FileHandler('logs/bot_debug.log')
    file_formatter = logging.Formatter(
        '%(asctime)s - BOT_DEBUG - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - DEBUG - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

def log_action(action: str, user_id: int = None, details: str = ""):
    """Простий логгер дій"""
    message = f"[{action}] User: {user_id} | {details}"
    logger.info(message)
    print(f"🔍 {message}")  # Додатково в консоль

def debug_callback(func):
    """Простий декоратор для callback'ів"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        user_id = "unknown"
        callback_data = "unknown"
        
        # Намагаємося отримати інформацію про користувача
        try:
            for arg in args:
                if hasattr(arg, 'from_user') and hasattr(arg.from_user, 'id'):
                    user_id = arg.from_user.id
                if hasattr(arg, 'data'):
                    callback_data = arg.data
                break
        except:
            pass
        
        try:
            log_action(f"START_{func_name}", user_id, f"data: {callback_data}")
            result = await func(*args, **kwargs)
            log_action(f"SUCCESS_{func_name}", user_id, f"data: {callback_data}")
            return result
        except Exception as e:
            log_action(f"ERROR_{func_name}", user_id, f"data: {callback_data}, error: {str(e)}")
            raise
    
    return wrapper

def log_state_transition(user_id: int, old_state: str, new_state: str, trigger: str):
    """Логування переходів між станами"""
    log_action("STATE_CHANGE", user_id, f"{old_state} → {new_state} ({trigger})")

def log_user_flow(user_id: int, step: str, data: dict = None):
    """Логування кроків user flow"""
    details = f"step: {step}"
    if data:
        details += f", data: {data}"
    log_action("USER_FLOW", user_id, details)

# Експортуємо основні функції
__all__ = ['log_action', 'debug_callback', 'log_state_transition', 'log_user_flow', 'logger']