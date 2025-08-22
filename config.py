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

# Повний список мов з прапорами для ВСІ підтримуваних мов
ALL_LANGUAGES_WITH_FLAGS = {
    # DeepL мови з прапорами
    "AR": "🇸🇦 العربية", "BG": "🇧🇬 Български", "CS": "🇨🇿 Čeština", 
    "DA": "🇩🇰 Dansk", "DE": "🇩🇪 Deutsch", "EL": "🇬🇷 Ελληνικά",
    "EN": "🇬🇧 English", "ES": "🇪🇸 Español", "ET": "🇪🇪 Eesti",
    "FI": "🇫🇮 Suomi", "FR": "🇫🇷 Français", "HE": "🇮🇱 עברית",
    "HU": "🇭🇺 Magyar", "ID": "🇮🇩 Bahasa Indonesia", "IT": "🇮🇹 Italiano",
    "JA": "🇯🇵 日本語", "KO": "🇰🇷 한국어", "LT": "🇱🇹 Lietuvių",
    "LV": "🇱🇻 Latviešu", "NB": "🇳🇴 Norsk", "NL": "🇳🇱 Nederlands",
    "PL": "🇵🇱 Polski", "PT": "🇵🇹 Português", "RO": "🇷🇴 Română",
    "RU": "🇷🇺 Русский", "SK": "🇸🇰 Slovenčina", "SL": "🇸🇮 Slovenščina",
    "SV": "🇸🇪 Svenska", "TH": "🇹🇭 ไทย", "TR": "🇹🇷 Türkçe",
    "UK": "🇺🇦 Українська", "VI": "🇻🇳 Tiếng Việt", "ZH": "🇨🇳 中文",
    
    # Додаткові O*Translator мови з прапорами
    "AF": "🇿🇦 Afrikaans", "SQ": "🇦🇱 Shqip", "AM": "🇪🇹 አማርኛ",
    "HY": "🇦🇲 Հայերեն", "AZ": "🇦🇿 Azərbaycan", "EU": "🏴󠁥󠁳󠁰󠁶󠁿 Euskera",
    "BE": "🇧🇾 Беларуская", "BN": "🇧🇩 বাংলা", "BS": "🇧🇦 Bosanski",
    "CA": "🏴󠁥󠁳󠁣󠁴󠁿 Català", "CO": "🇫🇷 Corsu", "HR": "🇭🇷 Hrvatski",
    "EO": "🌍 Esperanto", "TL": "🇵🇭 Filipino", "FY": "🇳🇱 Frysk",
    "GL": "🏴󠁥󠁳󠁧󠁡󠁿 Galego", "KA": "🇬🇪 ქართული", "GU": "🇮🇳 ગુજરાતી",
    "HT": "🇭🇹 Kreyòl", "HA": "🇳🇬 Hausa", "HAW": "🇺🇸 ʻŌlelo Hawaiʻi", "HI": "🇮🇳 हिन्दी",
    "HMN": "🇨🇳 Hmoob", "IS": "🇮🇸 Íslenska", "IG": "🇳🇬 Igbo",
    "GA": "🇮🇪 Gaeilge", "JW": "🇮🇩 Basa Jawa", "KN": "🇮🇳 ಕನ್ನಡ",
    "KK": "🇰🇿 Қазақ", "KM": "🇰🇭 ខ្មែរ", "RW": "🇷🇼 Kinyarwanda",
    "KU": "🇹🇷 Kurdî", "KY": "🇰🇬 Кыргызча", "LO": "🇱🇦 ລາວ",
    "LA": "🏛️ Latina", "LB": "🇱🇺 Lëtzebuergesch", "MK": "🇲🇰 Македонски",
    "MG": "🇲🇬 Malagasy", "MS": "🇲🇾 Bahasa Melayu", "ML": "🇮🇳 മലയാളം",
    "MT": "🇲🇹 Malti", "MI": "🇳🇿 Te Reo Māori", "MR": "🇮🇳 मराठी",
    "MN": "🇲🇳 Монгол", "MY": "🇲🇲 မြန်မာ", "NE": "🇳🇵 नेपाली",
    "NY": "🇲🇼 Chichewa", "OR": "🇮🇳 ଓଡ଼ିଆ", "PS": "🇦🇫 پښتو",
    "FA": "🇮🇷 فارسی", "PA": "🇮🇳 ਪੰਜਾਬੀ", "SM": "🇼🇸 Gagana Samoa",
    "GD": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Gàidhlig", "SR": "🇷🇸 Српски", "ST": "🇱🇸 Sesotho",
    "SN": "🇿🇼 Shona", "SD": "🇵🇰 سنڌي", "SI": "🇱🇰 සිංහල",
    "SO": "🇸🇴 Soomaali", "SU": "🇮🇩 Basa Sunda", "SW": "🇰🇪 Kiswahili",
    "TG": "🇹🇯 Тоҷикӣ", "TA": "🇱🇰 தமிழ்", "TT": "🇷🇺 Татар",
    "TE": "🇮🇳 తెలుగు", "TK": "🇹🇲 Türkmen", "UR": "🇵🇰 اردو",
    "UG": "🇨🇳 ئۇيغۇر", "UZ": "🇺🇿 O'zbek", "CY": "🏴󠁧󠁢󠁷󠁬󠁳󠁿 Cymraeg",
    "XH": "🇿🇦 isiXhosa", "YI": "🇮🇱 ייִדיש", "YO": "🇳🇬 Yorùbá",
    "ZU": "🇿🇦 isiZulu"
}

# Для зворотної сумісності
COMMON_LANGUAGES = ALL_LANGUAGES_WITH_FLAGS

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