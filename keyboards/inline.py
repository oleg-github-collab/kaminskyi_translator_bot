from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DEEPL_LANGUAGES, MODELS

def get_model_keyboard(user_lang: str = "en"):
    texts = {
        "uk": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "en": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "de": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "fr": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"},
        "es": {"basic": "⚡ Kaminskyi Basic", "epic": "🎯 Kaminskyi Epic"}
    }
    
    lang_texts = texts.get(user_lang, texts["en"])
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=lang_texts["basic"], callback_data="model_basic"),
        InlineKeyboardButton(text=lang_texts["epic"], callback_data="model_epic")
    )
    return keyboard

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for code, name in sorted(DEEPL_LANGUAGES.items()):
        buttons.append(InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
    keyboard.add(*buttons)
    return keyboard

def get_continue_keyboard(user_lang: str = "en"):
    texts = {
        "uk": {"continue": "Продовжити переклад", "exit": "Вийти"},
        "en": {"continue": "Continue translation", "exit": "Exit"},
        "de": {"continue": "Übersetzung fortsetzen", "exit": "Beenden"},
        "fr": {"continue": "Continuer la traduction", "exit": "Quitter"},
        "es": {"continue": "Continuar traducción", "exit": "Salir"}
    }
    
    lang_texts = texts.get(user_lang, texts["en"])
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text=lang_texts["continue"], callback_data="continue_translate"),
        InlineKeyboardButton(text=lang_texts["exit"], callback_data="exit")
    )
    return keyboard

def get_payment_keyboard(payment_url: str, user_lang: str = "en"):
    texts = {
        "uk": {"pay": "💳 Оплатити", "check": "🔄 Перевірити оплату"},
        "en": {"pay": "💳 Pay", "check": "🔄 Check payment"},
        "de": {"pay": "💳 Bezahlen", "check": "🔄 Zahlung prüfen"},
        "fr": {"pay": "💳 Payer", "check": "🔄 Vérifier le paiement"},
        "es": {"pay": "💳 Pagar", "check": "🔄 Verificar pago"}
    }
    
    lang_texts = texts.get(user_lang, texts["en"])
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=lang_texts["pay"], url=payment_url))
    keyboard.add(InlineKeyboardButton(text=lang_texts["check"], callback_data="check_payment"))
    return keyboard