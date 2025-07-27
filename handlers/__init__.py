from .start import register_handlers_start
from .language import register_handlers_language
from .file import register_handlers_file
from .payment import register_handlers_payment
from .translate import register_handlers_translate
import logging

logger = logging.getLogger(__name__)

def register_all_handlers(dp):
    """Реєстрація всіх handler'ів"""
    logger.info("=== РЕЄСТРАЦІЯ УСІХ HANDLER'ІВ ===")

    register_handlers_start(dp)
    logger.info("✅ Зареєстровано start handlers")

    register_handlers_language(dp)
    logger.info("✅ Зареєстровано language handlers")

    register_handlers_file(dp)
    logger.info("✅ Зареєстровано file handlers")

    register_handlers_payment(dp)
    logger.info("✅ Зареєстровано payment handlers")

    register_handlers_translate(dp)

    logger.info("✅ Зареєстровано translate handlers")

    logger.info("=== УСІ HANDLER'И ЗАРЕЄСТРОВАНО ===")


    logger.info("✅ Зареєстровано translate handlers")

    logger.info("=== УСІ HANDLER'И ЗАРЕЄСТРОВАНО ===")

    print("✅ Зареєстровано translate handlers")
    
    print("=== УСІ HANDLER'И ЗАРЕЄСТРОВАНО ===")


