import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from aiogram import types
from aiogram.dispatcher import FSMContext

logger = logging.getLogger(__name__)

class DebugLogger:
    """Детальний логгер для відлагодження user flow"""
    
    def __init__(self):
        self.setup_debug_logging()
    
    def setup_debug_logging(self):
        """Налаштування детального логування"""
        debug_logger = logging.getLogger('debug_flow')
        debug_logger.setLevel(logging.DEBUG)
        
        # Створюємо директорію logs якщо не існує
        import os
        os.makedirs('logs', exist_ok=True)
        
        # Створюємо окремий файл для debug логів
        debug_handler = logging.FileHandler('logs/debug_flow.log')
        debug_formatter = logging.Formatter(
            '%(asctime)s - DEBUG_FLOW - %(levelname)s - %(message)s'
        )
        debug_handler.setFormatter(debug_formatter)
        debug_logger.addHandler(debug_handler)
        
        self.debug_logger = debug_logger
    
    async def log_user_action(self, 
                            user_id: int, 
                            action: str, 
                            callback_data: Optional[str] = None,
                            state: Optional[FSMContext] = None,
                            message: Optional[types.Message] = None,
                            callback: Optional[types.CallbackQuery] = None,
                            additional_info: Dict[str, Any] = None):
        """Детальне логування дій користувача"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'callback_data': callback_data,
            'additional_info': additional_info or {}
        }
        
        # Отримуємо поточний стан
        if state:
            try:
                current_state = await state.get_state()
                user_data = await state.get_data()
                log_entry['current_state'] = current_state
                log_entry['user_data'] = user_data
            except Exception as e:
                log_entry['state_error'] = str(e)
        
        # Додаємо інформацію про повідомлення
        if message:
            log_entry['message_info'] = {
                'message_id': message.message_id,
                'chat_id': message.chat.id,
                'text': message.text[:100] if message.text else None,
                'content_type': message.content_type
            }
        
        # Додаємо інформацію про callback
        if callback:
            log_entry['callback_info'] = {
                'callback_id': callback.id,
                'data': callback.data,
                'from_user': callback.from_user.id if callback.from_user else None
            }
        
        self.debug_logger.info(f"USER_ACTION: {log_entry}")
        
        # Також в основний логгер
        logger.debug(f"[{action}] User {user_id}: {callback_data}")
    
    def log_handler_execution(self, handler_name: str, user_id: int, success: bool, 
                            error: Optional[str] = None, duration: Optional[float] = None):
        """Логування виконання handler'ів"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'handler': handler_name,
            'user_id': user_id,
            'success': success,
            'duration_ms': duration * 1000 if duration else None,
            'error': error
        }
        
        if success:
            self.debug_logger.info(f"HANDLER_SUCCESS: {log_entry}")
        else:
            self.debug_logger.error(f"HANDLER_ERROR: {log_entry}")
    
    def log_state_transition(self, user_id: int, from_state: str, to_state: str, 
                           trigger: str, success: bool = True):
        """Логування переходів між станами"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'from_state': from_state,
            'to_state': to_state,
            'trigger': trigger,
            'success': success
        }
        
        if success:
            self.debug_logger.info(f"STATE_TRANSITION: {log_entry}")
        else:
            self.debug_logger.error(f"STATE_TRANSITION_FAILED: {log_entry}")

# Глобальний екземпляр - ініціалізуємо безпечно
debug_logger = None

def get_debug_logger():
    """Безпечне отримання debug_logger з lazy ініціалізацією"""
    global debug_logger
    if debug_logger is None:
        try:
            debug_logger = DebugLogger()
        except Exception as e:
            # Fallback на простий логгер якщо проблеми з файлами
            import logging
            debug_logger = logging.getLogger('debug_flow_fallback')
            print(f"⚠️ Fallback debug logger: {e}")
    return debug_logger

# Ініціалізуємо при імпорті
debug_logger = get_debug_logger()

def debug_handler(handler_name: str):
    """Декоратор для логування handler'ів"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()
            user_id = None
            
            # Визначаємо user_id з аргументів
            try:
                for arg in args:
                    if hasattr(arg, 'from_user') and hasattr(arg.from_user, 'id'):
                        user_id = arg.from_user.id
                        break
            except:
                user_id = "unknown"
            
            try:
                # Безпечне логування початку виконання
                try:
                    if hasattr(debug_logger, 'debug_logger'):
                        debug_logger.debug_logger.debug(f"HANDLER_START: {handler_name} for user {user_id}")
                except:
                    print(f"DEBUG: HANDLER_START: {handler_name} for user {user_id}")
                
                # Виконуємо handler
                result = await func(*args, **kwargs)
                
                # Розрахунок тривалості
                duration = (datetime.now() - start_time).total_seconds()
                
                # Безпечне логування успішного завершення
                try:
                    if hasattr(debug_logger, 'log_handler_execution'):
                        debug_logger.log_handler_execution(handler_name, user_id, True, duration=duration)
                    else:
                        print(f"DEBUG: HANDLER_SUCCESS: {handler_name} for user {user_id} in {duration:.2f}s")
                except:
                    print(f"DEBUG: HANDLER_SUCCESS: {handler_name} for user {user_id}")
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                error_msg = f"{str(e)}"
                
                # Безпечне логування помилки
                try:
                    if hasattr(debug_logger, 'log_handler_execution'):
                        debug_logger.log_handler_execution(handler_name, user_id, False, error_msg, duration)
                    else:
                        print(f"DEBUG: HANDLER_ERROR: {handler_name} for user {user_id}: {error_msg}")
                except:
                    print(f"DEBUG: HANDLER_ERROR: {handler_name} for user {user_id}: {error_msg}")
                
                # Перекидаємо помилку далі
                raise
        
        return wrapper
    return decorator

async def log_callback_received(callback: types.CallbackQuery, state: FSMContext):
    """Логування отримання callback'у"""
    try:
        if hasattr(debug_logger, 'log_user_action'):
            await debug_logger.log_user_action(
                user_id=callback.from_user.id,
                action="callback_received",
                callback_data=callback.data,
                state=state,
                callback=callback
            )
        else:
            print(f"DEBUG: callback_received from user {callback.from_user.id}: {callback.data}")
    except:
        print(f"DEBUG: callback_received from user {callback.from_user.id}: {callback.data}")

async def log_message_received(message: types.Message, state: FSMContext):
    """Логування отримання повідомлення"""
    try:
        if hasattr(debug_logger, 'log_user_action'):
            await debug_logger.log_user_action(
                user_id=message.from_user.id,
                action="message_received",
                state=state,
                message=message
            )
        else:
            print(f"DEBUG: message_received from user {message.from_user.id}")
    except:
        print(f"DEBUG: message_received from user {message.from_user.id}")

async def log_state_change(user_id: int, state: FSMContext, old_state: str, new_state: str, trigger: str):
    """Логування зміни стану"""
    try:
        if hasattr(debug_logger, 'log_state_transition'):
            debug_logger.log_state_transition(user_id, old_state, new_state, trigger)
        
        if hasattr(debug_logger, 'log_user_action'):
            await debug_logger.log_user_action(
                user_id=user_id,
                action="state_change",
                state=state,
                additional_info={
                    'old_state': old_state,
                    'new_state': new_state,
                    'trigger': trigger
                }
            )
        else:
            print(f"DEBUG: state_change for user {user_id}: {old_state} → {new_state} ({trigger})")
    except:
        print(f"DEBUG: state_change for user {user_id}: {old_state} → {new_state} ({trigger})")

def get_current_user_flow_status(user_id: int) -> Dict[str, Any]:
    """Отримання поточного статусу user flow"""
    # Можна додати аналіз логів для визначення стану користувача
    return {
        'user_id': user_id,
        'last_action': 'unknown',
        'timestamp': datetime.now().isoformat()
    }

# Middleware для автоматичного логування всіх запитів
try:
    from aiogram.dispatcher.middlewares import BaseMiddleware
    
    class DebugMiddleware(BaseMiddleware):
        """Middleware для автоматичного логування"""
        
        def __init__(self):
            super().__init__()
        
        async def on_process_message(self, message: types.Message, data: dict):
            """Обробка вхідних повідомлень"""
            try:
                state = data.get('state')
                if state:
                    await log_message_received(message, state)
            except Exception as e:
                print(f"DEBUG: Middleware message error: {e}")
        
        async def on_process_callback_query(self, callback: types.CallbackQuery, data: dict):
            """Обробка callback запитів"""
            try:
                state = data.get('state')
                if state:
                    await log_callback_received(callback, state)
            except Exception as e:
                print(f"DEBUG: Middleware callback error: {e}")

except ImportError:
    # Fallback якщо aiogram не доступний
    class DebugMiddleware:
        def __init__(self):
            pass