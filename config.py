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
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:8000/webhook")
PORT = int(os.getenv("PORT", 8000))

# Languages - DeepL API Supported Languages (2025)
DEEPL_LANGUAGES = {
    "AR": "Arabic", "BG": "Bulgarian", "CS": "Czech", "DA": "Danish", 
    "DE": "German", "EL": "Greek", "EN": "English", "ES": "Spanish", 
    "ET": "Estonian", "FI": "Finnish", "FR": "French", "HE": "Hebrew",
    "HU": "Hungarian", "ID": "Indonesian", "IT": "Italian", "JA": "Japanese",
    "KO": "Korean", "LT": "Lithuanian", "LV": "Latvian", "NB": "Norwegian",
    "NL": "Dutch", "PL": "Polish", "PT": "Portuguese", "RO": "Romanian",
    "RU": "Russian", "SK": "Slovak", "SL": "Slovenian", "SV": "Swedish",
    "TH": "Thai", "TR": "Turkish", "UK": "Ukrainian", "VI": "Vietnamese",
    "ZH": "Chinese"
}

# O*Translator Languages (80+ languages supported)
OTRANSLATOR_LANGUAGES = {
    "AF": "Afrikaans", "SQ": "Albanian", "AM": "Amharic", "AR": "Arabic",
    "HY": "Armenian", "AZ": "Azerbaijani", "EU": "Basque", "BE": "Belarusian",
    "BN": "Bengali", "BS": "Bosnian", "BG": "Bulgarian", "CA": "Catalan",
    "ZH": "Chinese", "CO": "Corsican", "HR": "Croatian", "CS": "Czech",
    "DA": "Danish", "NL": "Dutch", "EN": "English", "EO": "Esperanto",
    "ET": "Estonian", "TL": "Filipino", "FI": "Finnish", "FR": "French",
    "FY": "Frisian", "GL": "Galician", "KA": "Georgian", "DE": "German",
    "EL": "Greek", "GU": "Gujarati", "HT": "Haitian", "HA": "Hausa",
    "HAW": "Hawaiian", "HE": "Hebrew", "HI": "Hindi", "HMN": "Hmong",
    "HU": "Hungarian", "IS": "Icelandic", "IG": "Igbo", "ID": "Indonesian",
    "GA": "Irish", "IT": "Italian", "JA": "Japanese", "JW": "Javanese",
    "KN": "Kannada", "KK": "Kazakh", "KM": "Khmer", "RW": "Kinyarwanda",
    "KO": "Korean", "KU": "Kurdish", "KY": "Kyrgyz", "LO": "Lao",
    "LA": "Latin", "LV": "Latvian", "LT": "Lithuanian", "LB": "Luxembourgish",
    "MK": "Macedonian", "MG": "Malagasy", "MS": "Malay", "ML": "Malayalam",
    "MT": "Maltese", "MI": "Maori", "MR": "Marathi", "MN": "Mongolian",
    "MY": "Myanmar", "NE": "Nepali", "NB": "Norwegian", "NY": "Nyanja",
    "OR": "Odia", "PS": "Pashto", "FA": "Persian", "PL": "Polish",
    "PT": "Portuguese", "PA": "Punjabi", "RO": "Romanian", "RU": "Russian",
    "SM": "Samoan", "GD": "Scottish", "SR": "Serbian", "ST": "Sesotho",
    "SN": "Shona", "SD": "Sindhi", "SI": "Sinhala", "SK": "Slovak",
    "SL": "Slovenian", "SO": "Somali", "ES": "Spanish", "SU": "Sundanese",
    "SW": "Swahili", "SV": "Swedish", "TG": "Tajik", "TA": "Tamil",
    "TT": "Tatar", "TE": "Telugu", "TH": "Thai", "TR": "Turkish",
    "TK": "Turkmen", "UK": "Ukrainian", "UR": "Urdu", "UG": "Uyghur",
    "UZ": "Uzbek", "VI": "Vietnamese", "CY": "Welsh", "XH": "Xhosa",
    "YI": "Yiddish", "YO": "Yoruba", "ZU": "Zulu"
}

# Combined languages for interface (most commonly used)
COMMON_LANGUAGES = {
    "UK": "🇺🇦 Українська", "EN": "🇬🇧 English", "DE": "🇩🇪 Deutsch", 
    "FR": "🇫🇷 Français", "ES": "🇪🇸 Español", "PL": "🇵🇱 Polski",
    "RU": "🇷🇺 Русский", "ZH": "🇨🇳 中文", "JA": "🇯🇵 日本語",
    "AR": "🇸🇦 العربية", "IT": "🇮🇹 Italiano", "PT": "🇵🇹 Português",
    "NL": "🇳🇱 Nederlands", "SV": "🇸🇪 Svenska", "DA": "🇩🇰 Dansk",
    "NB": "🇳🇴 Norsk", "FI": "🇫🇮 Suomi", "HU": "🇭🇺 Magyar",
    "CS": "🇨🇿 Čeština", "SK": "🇸🇰 Slovenčina", "BG": "🇧🇬 Български",
    "RO": "🇷🇴 Română", "EL": "🇬🇷 Ελληνικά", "TR": "🇹🇷 Türkçe",
    "HI": "🇮🇳 हिन्दी", "KO": "🇰🇷 한국어", "TH": "🇹🇭 ไทย",
    "VI": "🇻🇳 Tiếng Việt", "ID": "🇮🇩 Bahasa Indonesia", "MS": "🇲🇾 Bahasa Melayu",
    "HE": "🇮🇱 עברית", "FA": "🇮🇷 فارسی"
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