import logging
from typing import Optional, Dict, Any
from aiogram import types
from aiogram.dispatcher import FSMContext
from states import TranslationStates
try:
    from utils.debug_logger import debug_logger, log_state_change
except ImportError:
    debug_logger = None
    async def log_state_change(*args, **kwargs):
        print(f"DEBUG: State change fallback: {args}")

logger = logging.getLogger(__name__)

class FlowManager:
    """Централізований менеджер для керування user flow"""
    
    def __init__(self):
        self.current_users = {}  # Зберігає стан користувачів
    
    async def safe_state_transition(self, user_id: int, state: FSMContext, 
                                  target_state: str, trigger: str = "system") -> bool:
        """Безпечний перехід між станами з логуванням"""
        try:
            old_state = await state.get_state()
            
            if target_state == "choosing_model":
                await TranslationStates.choosing_model.set()
            elif target_state == "waiting_for_source_language":
                await TranslationStates.waiting_for_source_language.set()
            elif target_state == "waiting_for_target_language":
                await TranslationStates.waiting_for_target_language.set()
            elif target_state == "waiting_for_file":
                await TranslationStates.waiting_for_file.set()
            elif target_state == "waiting_for_payment_confirmation":
                await TranslationStates.waiting_for_payment_confirmation.set()
            elif target_state == "translating":
                await TranslationStates.translating.set()
            elif target_state == "completed":
                await TranslationStates.completed.set()
            else:
                logger.error(f"Unknown target state: {target_state}")
                return False
            
            new_state = await state.get_state()
            
            # Логування успішного переходу
            await log_state_change(user_id, state, old_state or "none", new_state, trigger)
            logger.info(f"✅ State transition: {old_state} → {new_state} for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ State transition failed for user {user_id}: {str(e)}")
            return False
    
    async def get_user_progress(self, user_id: int, state: FSMContext) -> Dict[str, Any]:
        """Отримання прогресу користувача"""
        try:
            current_state = await state.get_state()
            user_data = await state.get_data()
            
            progress = {
                'user_id': user_id,
                'current_state': current_state,
                'step': self._get_step_number(current_state),
                'completed_steps': [],
                'data': user_data
            }
            
            # Визначаємо завершені кроки
            if user_data.get('model'):
                progress['completed_steps'].append('model_selected')
            if user_data.get('source_language'):
                progress['completed_steps'].append('source_language_selected')
            if user_data.get('target_language'):
                progress['completed_steps'].append('target_language_selected')
            if user_data.get('file_path'):
                progress['completed_steps'].append('file_uploaded')
            if user_data.get('payment_completed'):
                progress['completed_steps'].append('payment_completed')
            
            return progress
            
        except Exception as e:
            logger.error(f"❌ Error getting user progress for {user_id}: {str(e)}")
            return {'user_id': user_id, 'error': str(e)}
    
    def _get_step_number(self, state_name: str) -> int:
        """Отримання номера кроку за станом"""
        state_steps = {
            'TranslationStates:choosing_model': 1,
            'TranslationStates:waiting_for_source_language': 2,
            'TranslationStates:waiting_for_target_language': 3,
            'TranslationStates:waiting_for_file': 4,
            'TranslationStates:waiting_for_payment_confirmation': 5,
            'TranslationStates:translating': 6,
            'TranslationStates:completed': 7
        }
        return state_steps.get(state_name, 0)
    
    async def validate_user_data(self, user_id: int, state: FSMContext) -> Dict[str, bool]:
        """Валідація даних користувача"""
        try:
            user_data = await state.get_data()
            
            validation = {
                'has_model': bool(user_data.get('model')),
                'has_source_language': bool(user_data.get('source_language')),
                'has_target_language': bool(user_data.get('target_language')),
                'has_file': bool(user_data.get('file_path')),
                'languages_different': user_data.get('source_language') != user_data.get('target_language'),
                'valid_model': user_data.get('model') in ['basic', 'epic'],
                'all_valid': False
            }
            
            validation['all_valid'] = (
                validation['has_model'] and
                validation['has_source_language'] and
                validation['has_target_language'] and
                validation['has_file'] and
                validation['languages_different'] and
                validation['valid_model']
            )
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Validation error for user {user_id}: {str(e)}")
            return {'all_valid': False, 'error': str(e)}
    
    async def reset_user_completely(self, user_id: int, state: FSMContext):
        """Повне скидання користувача"""
        try:
            await state.finish()
            await state.reset_data()
            if user_id in self.current_users:
                del self.current_users[user_id]
            logger.info(f"✅ Complete reset for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Reset error for user {user_id}: {str(e)}")
    
    async def handle_error_recovery(self, user_id: int, state: FSMContext, error: str):
        """Відновлення після помилки"""
        try:
            logger.warning(f"🔄 Error recovery for user {user_id}: {error}")
            
            # Отримуємо поточний стан
            current_state = await state.get_state()
            user_data = await state.get_data()
            
            # Логіка відновлення залежно від стану
            if not current_state:
                # Якщо стан втрачено - повертаємо до початку
                await self.safe_state_transition(user_id, state, "choosing_model", "error_recovery")
                return "restarted"
            
            # Якщо є частково заповнені дані - пропонуємо продовжити
            if user_data.get('model') and not user_data.get('source_language'):
                await self.safe_state_transition(user_id, state, "waiting_for_source_language", "error_recovery")
                return "restored_to_language_selection"
            
            if user_data.get('target_language') and not user_data.get('file_path'):
                await self.safe_state_transition(user_id, state, "waiting_for_file", "error_recovery")
                return "restored_to_file_upload"
            
            # За замовчуванням - повний перезапуск
            await self.reset_user_completely(user_id, state)
            await self.safe_state_transition(user_id, state, "choosing_model", "error_recovery_restart")
            return "full_restart"
            
        except Exception as e:
            logger.error(f"❌ Recovery failed for user {user_id}: {str(e)}")
            return "recovery_failed"
    
    async def send_progress_message(self, user_id: int, state: FSMContext, 
                                  message_target: types.Message) -> bool:
        """Відправка повідомлення з прогресом"""
        try:
            progress = await self.get_user_progress(user_id, state)
            
            progress_text = f"📊 <b>Ваш прогрес:</b>\n\n"
            progress_text += f"👤 Крок {progress['step']}/7\n"
            progress_text += f"✅ Завершено: {len(progress['completed_steps'])}/7\n\n"
            
            # Детальний прогрес
            steps_status = {
                'model_selected': '1. ⚙️ Модель обрана',
                'source_language_selected': '2. 🔤 Мова оригіналу',
                'target_language_selected': '3. 🌐 Мова перекладу',
                'file_uploaded': '4. 📄 Файл завантажено',
                'payment_completed': '5. 💳 Оплата завершена'
            }
            
            for step_key, step_text in steps_status.items():
                if step_key in progress['completed_steps']:
                    progress_text += f"✅ {step_text}\n"
                else:
                    progress_text += f"⏳ {step_text}\n"
            
            await message_target.answer(progress_text, parse_mode="HTML")
            return True
            
        except Exception as e:
            logger.error(f"❌ Progress message failed for user {user_id}: {str(e)}")
            return False

# Глобальний екземпляр
flow_manager = FlowManager()

async def safe_callback_handler(callback: types.CallbackQuery, state: FSMContext, 
                               handler_func, handler_name: str) -> bool:
    """Безпечний wrapper для callback handler'ів"""
    user_id = callback.from_user.id
    
    try:
        # Безпечне логування початку
        try:
            if debug_logger and hasattr(debug_logger, 'log_user_action'):
                await debug_logger.log_user_action(
                    user_id=user_id,
                    action=f"handler_start_{handler_name}",
                    callback_data=callback.data,
                    state=state,
                    callback=callback
                )
        except:
            print(f"DEBUG: handler_start_{handler_name} for user {user_id}")
        
        # Виконання handler'а
        result = await handler_func(callback, state)
        
        # Безпечне логування успіху
        try:
            if debug_logger and hasattr(debug_logger, 'log_user_action'):
                await debug_logger.log_user_action(
                    user_id=user_id,
                    action=f"handler_success_{handler_name}",
                    callback_data=callback.data,
                    state=state,
                    additional_info={'result': 'success'}
                )
        except:
            print(f"DEBUG: handler_success_{handler_name} for user {user_id}")
        
        return True
        
    except Exception as e:
        # Безпечне логування помилки
        error_msg = str(e)
        try:
            if debug_logger and hasattr(debug_logger, 'log_user_action'):
                await debug_logger.log_user_action(
                    user_id=user_id,
                    action=f"handler_error_{handler_name}",
                    callback_data=callback.data,
                    state=state,
                    additional_info={'error': error_msg}
                )
        except:
            print(f"DEBUG: handler_error_{handler_name} for user {user_id}: {error_msg}")
        
        # Спроба відновлення
        recovery_result = await flow_manager.handle_error_recovery(user_id, state, error_msg)
        
        # Повідомлення користувачу
        await callback.answer("⚠️ Сталася помилка, відновлюємо...")
        
        if recovery_result == "restarted":
            await callback.message.answer("🔄 Перезапускаємо процес. Оберіть модель:")
        elif recovery_result == "recovery_failed":
            await callback.message.answer("❌ Помилка відновлення. Натисніть /start")
        
        return False

# Utility функції
async def ensure_valid_state(user_id: int, state: FSMContext, required_state: str = None) -> bool:
    """Перевірка та забезпечення правильного стану"""
    try:
        current_state = await state.get_state()
        
        if required_state and current_state != required_state:
            logger.warning(f"⚠️ State mismatch for user {user_id}: {current_state} != {required_state}")
            return False
        
        if not current_state:
            logger.warning(f"⚠️ No state for user {user_id}")
            await flow_manager.safe_state_transition(user_id, state, "choosing_model", "ensure_valid_state")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ State validation error for user {user_id}: {str(e)}")
        return False