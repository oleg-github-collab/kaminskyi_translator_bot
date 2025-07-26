from aiogram.dispatcher.filters.state import State, StatesGroup

class TranslationStates(StatesGroup):
    choosing_model = State()
    waiting_for_source_language = State()
    waiting_for_target_language = State()
    waiting_for_file = State()
    waiting_for_payment_confirmation = State()
    translating = State()
    completed = State()