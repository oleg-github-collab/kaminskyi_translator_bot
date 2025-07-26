from .start import register_handlers_start
from .language import register_handlers_language
from .file import register_handlers_file
from .file_actions import register_handlers_file_actions
from .payment import register_handlers_payment
from .translate import register_handlers_translate

def register_all_handlers(dp):
    register_handlers_start(dp)
    register_handlers_language(dp)
    register_handlers_file(dp)
    register_handlers_file_actions(dp)
    register_handlers_payment(dp)
    register_handlers_translate(dp)