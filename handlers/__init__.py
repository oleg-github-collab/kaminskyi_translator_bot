from .start import register_handlers_start
from .language import register_handlers_language
from .file import register_handlers_file
from .payment import register_handlers_payment
from .translate import register_handlers_translate
from .universal import register_handlers_universal

def register_all_handlers(dp):
    """РЕЄСТРАЦІЯ УСІХ HANDLER'ІВ З УНІВЕРСАЛЬНИМ FALLBACK"""
    print("=== РЕЄСТРАЦІЯ УСІХ HANDLER'ІВ ===")
    
    # Специфічні handler'и (високий пріоритет)
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
    
    # Універсальний handler (найнижчий пріоритет - fallback)
    register_handlers_universal(dp)
    print("✅ Зареєстровано universal fallback handler")
    
    print("=== УСІ HANDLER'И ЗАРЕЄСТРОВАНО ===")