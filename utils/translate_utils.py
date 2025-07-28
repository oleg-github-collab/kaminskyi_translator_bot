import requests
import time
import config
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def translate_text_deepl(text: str, target_lang: str, source_lang: str = None) -> str:
    """Translate text using DeepL API"""
    if not text.strip():
        return ""
        
    url = "https://api-free.deepl.com/v2/translate"
    headers = {"Authorization": f"DeepL-Auth-Key {config.DEEPL_API_KEY}"}
    
    data = {
        "text": text,
        "target_lang": target_lang.upper()
    }
    
    if source_lang:
        data["source_lang"] = source_lang.upper()
    
    try:
        logger.info(f"Starting DeepL translation: {len(text)} chars, {source_lang} -> {target_lang}")
        
        response = requests.post(
            url,
            headers=headers,
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()["translations"][0]["text"]
            logger.info("DeepL translation completed successfully")
            return result
        else:
            error_msg = f"DeepL API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(f"Помилка API: {response.status_code}")
            
    except requests.exceptions.Timeout:
        logger.error("DeepL translation timeout")
        raise Exception("Час очікування перекладу вичерпано")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during DeepL translation: {str(e)}")
        raise Exception(f"Помилка мережі: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during DeepL translation: {str(e)}")
        raise Exception(f"Помилка перекладу: {str(e)}")


def fetch_deepl_languages() -> Dict[str, str]:
    """Fetch available target languages from DeepL"""
    if not config.DEEPL_API_KEY:
        return config.DEEPL_LANGUAGES

    try:
        response = requests.get(
            "https://api-free.deepl.com/v2/languages",
            params={"type": "target"},
            headers={"Authorization": f"DeepL-Auth-Key {config.DEEPL_API_KEY}"},
            timeout=30,
        )
        if response.status_code == 200:
            languages = {
                lang["language"].upper(): lang.get("name", lang["language"])
                for lang in response.json()
            }
            return languages or config.DEEPL_LANGUAGES
        logger.error(
            f"Failed to fetch DeepL languages: {response.status_code} {response.text}"
        )
    except Exception as e:
        logger.error(f"Error fetching DeepL languages: {str(e)}")

    return config.DEEPL_LANGUAGES


def fetch_otranslator_languages() -> Dict[str, str]:
    """Fetch available languages from O*Translator"""
    if not config.OTRANSLATOR_API_KEY:
        return config.OTRANSLATOR_LANGUAGES

    try:
        response = requests.get(
            f"{config.OTRANSLATOR_API_URL}/languages",
            headers={"Authorization": f"Bearer {config.OTRANSLATOR_API_KEY}"},
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            languages = {
                item["code"].upper(): item.get("name", item["code"])
                for item in data.get("languages", [])
            }
            return languages or config.OTRANSLATOR_LANGUAGES
        logger.error(
            f"Failed to fetch OTranslator languages: {response.status_code} {response.text}"
        )
    except Exception as e:
        logger.error(f"Error fetching OTranslator languages: {str(e)}")

    return config.OTRANSLATOR_LANGUAGES

    return config.OTRANSLATOR_LANGUAGES
    return config.OTRANSLATOR_LANGUAGES
    return config.OTRANSLATOR_LANGUAGES
    return config.OTRANSLATOR_LANGUAGES
    return {}


