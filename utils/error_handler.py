import logging
import traceback
from functools import wraps
from typing import Callable, Any
from aiogram import types
from aiogram.dispatcher import FSMContext

logger = logging.getLogger(__name__)

def payment_error_handler(func: Callable) -> Callable:
    """Декоратор для обробки помилок у платіжних функціях"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Логування детальної помилки
            error_details = {
                'function': func.__name__,
                'args': str(args)[:200],
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            logger.error(f"Payment error in {func.__name__}: {error_details}")
            
            # Отримуємо callback та відправляємо повідомлення користувачу
            callback = None
            for arg in args:
                if isinstance(arg, types.CallbackQuery):
                    callback = arg
                    break
            
            if callback:
                try:
                    await callback.answer("⚠️ Виникла технічна помилка")
                    await callback.message.answer(
                        "❌ <b>Технічна помилка</b>\n\n"
                        "Вибачте, сталася помилка при обробці платежу. "
                        "Спробуйте ще раз або зверніться до підтримки.\n\n"
                        f"🆔 <b>ID помилки:</b> <code>{func.__name__}_{hash(str(e)) % 10000}</code>",
                        parse_mode="HTML"
                    )
                except Exception as notify_error:
                    logger.error(f"Failed to notify user about error: {notify_error}")
            
            # Не перериваємо виконання, повертаємо None
            return None
    return wrapper

def log_payment_action(action: str, user_id: int, details: dict = None):
    """Логування платіжних дій"""
    log_entry = {
        'action': action,
        'user_id': user_id,
        'timestamp': __import__('time').time(),
        'details': details or {}
    }
    logger.info(f"Payment action: {log_entry}")

def validate_payment_data(data: dict) -> bool:
    """Валідація платіжних даних"""
    required_fields = ['char_count', 'model', 'amount']
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required payment field: {field}")
            return False
    
    # Перевірка типів даних
    if not isinstance(data['char_count'], (int, float)) or data['char_count'] <= 0:
        logger.warning(f"Invalid char_count: {data['char_count']}")
        return False
    
    if data['model'] not in ['basic', 'epic']:
        logger.warning(f"Invalid model: {data['model']}")
        return False
    
    if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        logger.warning(f"Invalid amount: {data['amount']}")
        return False
    
    return True

def sanitize_user_input(text: str) -> str:
    """Очищення користувацького вводу"""
    if not isinstance(text, str):
        return ""
    
    # Видаляємо потенційно небезпечні символи
    dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Обмежуємо довжину
    return text[:1000]

async def safe_state_update(state: FSMContext, **data):
    """Безпечне оновлення стану з логуванням"""
    try:
        await state.update_data(**data)
        logger.debug(f"State updated with keys: {list(data.keys())}")
    except Exception as e:
        logger.error(f"Failed to update state: {str(e)}")
        raise

class PaymentValidator:
    """Клас для валідації платіжних операцій"""
    
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 1000.0) -> bool:
        """Валідація суми платежу"""
        return min_amount <= amount <= max_amount
    
    @staticmethod
    def validate_currency(currency: str) -> bool:
        """Валідація валюти"""
        allowed_currencies = ['EUR', 'USD', 'UAH']
        return currency.upper() in allowed_currencies
    
    @staticmethod
    def validate_user_id(user_id: int) -> bool:
        """Валідація ID користувача"""
        return isinstance(user_id, int) and user_id > 0
    
    @staticmethod
    def validate_session_data(session_data: dict) -> tuple[bool, str]:
        """Комплексна валідація даних сесії"""
        if not isinstance(session_data, dict):
            return False, "Session data must be a dictionary"
        
        required_fields = ['user_id', 'amount', 'currency', 'char_count', 'model']
        for field in required_fields:
            if field not in session_data:
                return False, f"Missing required field: {field}"
        
        if not PaymentValidator.validate_user_id(session_data['user_id']):
            return False, "Invalid user ID"
        
        if not PaymentValidator.validate_amount(session_data['amount']):
            return False, "Invalid amount"
        
        if not PaymentValidator.validate_currency(session_data['currency']):
            return False, "Invalid currency"
        
        return True, "Valid"

# Глобальний обробник помилок для всього модуля платежів
def setup_payment_error_logging():
    """Налаштування логування помилок для платіжного модуля"""
    payment_logger = logging.getLogger('payment')
    payment_logger.setLevel(logging.DEBUG)
    
    # Створюємо окремий файл для логів платежів
    handler = logging.FileHandler('logs/payment.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    payment_logger.addHandler(handler)
    
    return payment_logger