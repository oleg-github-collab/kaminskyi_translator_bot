import requests
import time
import config
import logging
from typing import Optional

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