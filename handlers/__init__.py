from .start import register_handlers_start
from .language import register_handlers_language
from .file import register_handlers_file
from .payment import register_handlers_payment
from .translate import register_handlers_translate

def register_all_handlers(dp):
    """РЕЄСТРАЦІЯ УСІХ HANDLER'ІВ"""
    print("=== РЕЄСТРАЦІЯ УСІХ HANDLER'ІВ ===")  # ДЕБАГ
    
    register_handlers_start(dp)
    print("✅ Зареєстровано start handlers")
    
    register_handlers_language(dp)
    print("✅ Зареєстровано language handlers")
    
    register_handlers_file(dp)
    print("✅ Зареєстровано file handlers")
    
    register_handlers_payment(dp)
    print("✅ Зареєстровано payment handlers")
    
    register_handlers_translate(dp)
    print("✅ Зареєстровано translate handlers")
    
    print("=== УСІ HANDLER'И ЗАРЕЄСТРОВАНО ===")
