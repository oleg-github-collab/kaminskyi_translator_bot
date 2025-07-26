from .start import register_handlers_start
from .language import register_handlers_language
from .file import register_handlers_file
from .payment import register_handlers_payment

def register_all_handlers(dp):
    # Правильний порядок реєстрації
    register_handlers_file(dp)
    register_handlers_payment(dp)
    register_handlers_language(dp)
    register_handlers_start(dp)