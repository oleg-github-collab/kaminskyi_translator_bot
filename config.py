import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API Keys
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
OTRANSLATOR_API_KEY = os.getenv("OTRANSLATOR_API_KEY")

# Webhook
WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://kaminskyitranslatorbot-production.up.railway.app",
)
# Some environments may include '/webhook' in WEBHOOK_URL from older configs
if WEBHOOK_URL.endswith("/webhook"):
    WEBHOOK_URL = WEBHOOK_URL.rsplit("/webhook", 1)[0]

# Some environments may include '/webhook' in WEBHOOK_URL from older configs
if WEBHOOK_URL.endswith("/webhook"):
    WEBHOOK_URL = WEBHOOK_URL.rsplit("/webhook", 1)[0]
PORT = int(os.getenv("PORT", 8000))

# Languages
DEEPL_LANGUAGES = {
    "BG": "Bulgarian", "CS": "Czech", "DA": "Danish", "DE": "German",
    "EL": "Greek", "EN": "English", "ES": "Spanish", "ET": "Estonian",
    "FI": "Finnish", "FR": "French", "HU": "Hungarian", "ID": "Indonesian",
    "IT": "Italian", "JA": "Japanese", "KO": "Korean", "LT": "Lithuanian",
    "LV": "Latvian", "NB": "Norwegian", "NL": "Dutch", "PL": "Polish",
    "PT": "Portuguese", "RO": "Romanian", "RU": "Russian", "SK": "Slovak",
    "SL": "Slovenian", "SV": "Swedish", "TR": "Turkish", "UK": "Ukrainian",
    "ZH": "Chinese"
}

# Fallback languages for O*Translator if API call fails
OTRANSLATOR_LANGUAGES = {
    "AR": "Arabic",
    "BE": "Belarusian",
    "BG": "Bulgarian",
    "CS": "Czech",
    "DA": "Danish",
    "DE": "German",
    "EL": "Greek",
    "EN": "English",
    "ES": "Spanish",
    "ET": "Estonian",
    "FI": "Finnish",
    "FR": "French",
    "HE": "Hebrew",
    "HI": "Hindi",
    "HR": "Croatian",
    "HU": "Hungarian",
    "ID": "Indonesian",
    "IT": "Italian",
    "JA": "Japanese",
    "KA": "Georgian",
    "KK": "Kazakh",
    "KO": "Korean",
    "LT": "Lithuanian",
    "LV": "Latvian",
    "NB": "Norwegian",
    "NL": "Dutch",
    "PL": "Polish",
    "PT": "Portuguese",
    "RO": "Romanian",
    "RU": "Russian",
    "SK": "Slovak",
    "SL": "Slovenian",
    "SR": "Serbian",
    "SV": "Swedish",
    "TH": "Thai",
    "TR": "Turkish",
    "UK": "Ukrainian",
    "UZ": "Uzbek",
    "VI": "Vietnamese",
    "ZH": "Chinese",
}

INTERFACE_LANGUAGES = {
    "uk": "Українська",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español"
}

# Pricing
BASIC_PRICE_PER_1860_CHARS = 0.65  # €
EPIC_PRICE_PER_1860_CHARS = 0.95   # €
MIN_PRICE_BASIC = 0.65             # €
MIN_PRICE_EPIC = 2.50              # €
CHARS_PER_UNIT = 1860

# Models
MODELS = {
    "basic": {
        "name": "Kaminskyi Basic",
        "description": "⚡ Блискавичний переклад через DeepL",
        "api": "deepl",
        "price_per_unit": BASIC_PRICE_PER_1860_CHARS,
        "min_price": MIN_PRICE_BASIC
    },
    "epic": {
        "name": "Kaminskyi Epic",
        "description": "🎯 Найкраща якість через Gemini 2.5 Flash",
        "api": "otranslator",
        "model": "gemini-2.5-flash",
        "price_per_unit": EPIC_PRICE_PER_1860_CHARS,
        "min_price": MIN_PRICE_EPIC
    }
}

# Directories
TEMP_DIR = "temp"
LOGS_DIR = "logs"

# O*Translator settings
OTRANSLATOR_API_URL = "https://otranslator.com/uk/developer/v1"
OTRANSLATOR_MODEL = "gemini-2.5-flash"
