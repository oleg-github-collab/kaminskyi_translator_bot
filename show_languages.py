#!/usr/bin/env python3
"""
Показати всі доступні мови
"""

# DeepL Languages (29 мов)
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

# O*Translator Languages (80+ мов)
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

# Common Languages з прапорами
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

def show_all_languages():
    """Показати всі мови"""
    print("🌍 === ДОСТУПНІ МОВИ ДЛЯ ПЕРЕКЛАДУ ===\n")
    
    print("⚡ KAMINSKYI BASIC (DeepL API) - 29 мов:")
    print("=" * 50)
    deepl_sorted = sorted(DEEPL_LANGUAGES.items(), key=lambda x: x[1])
    for i, (code, name) in enumerate(deepl_sorted, 1):
        display = COMMON_LANGUAGES.get(code, name)
        print(f"{i:2d}. {code}: {display}")
    
    print(f"\n🎯 KAMINSKYI EPIC (O*Translator API) - {len(OTRANSLATOR_LANGUAGES)} мов:")
    print("=" * 50)
    otrans_sorted = sorted(OTRANSLATOR_LANGUAGES.items(), key=lambda x: x[1])
    
    # Показуємо по 3 в рядку для компактності
    for i in range(0, len(otrans_sorted), 3):
        row = otrans_sorted[i:i+3]
        line_parts = []
        for j, (code, name) in enumerate(row):
            display = COMMON_LANGUAGES.get(code, name)
            if len(display) > 15:
                display = display[:12] + "..."
            line_parts.append(f"{code}: {display:15}")
        print("  ".join(line_parts))
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   • DeepL API: {len(DEEPL_LANGUAGES)} мов")
    print(f"   • O*Translator API: {len(OTRANSLATOR_LANGUAGES)} мов") 
    print(f"   • З прапорами: {len(COMMON_LANGUAGES)} мов")
    print(f"   • Нові мови DeepL: Arabic, Hebrew, Thai, Vietnamese")
    print(f"   • Унікальні мови O*Translator: {len(set(OTRANSLATOR_LANGUAGES.keys()) - set(DEEPL_LANGUAGES.keys()))} додаткових")

if __name__ == "__main__":
    show_all_languages()