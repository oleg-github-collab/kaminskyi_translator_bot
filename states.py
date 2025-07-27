from aiogram.dispatcher.filters.state import State, StatesGroup

class TranslationStates(StatesGroup):
    """Стани процесу перекладу"""
    
    # Крок 1: Вибір моделі (Basic/Epic)
    choosing_model = State()
    
    # Крок 2: Вибір мови оригіналу
    waiting_for_source_language = State()
    
    # Крок 3: Вибір мови перекладу
    waiting_for_target_language = State()
    
    # Крок 4: Очікування файлу
    waiting_for_file = State()
    
    # Крок 5: Очікування підтвердження оплати
    waiting_for_payment_confirmation = State()
    
    # Процес перекладу
    translating = State()
    
    # Переклад завершено
    completed = State()
