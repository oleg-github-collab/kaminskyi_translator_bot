import requests
import time
import config
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def validate_language_for_otranslator(lang_code: str) -> bool:
    """Перевірити чи підтримує O*Translator вказану мову"""
    return lang_code.upper() in config.OTRANSLATOR_LANGUAGES

def translate_file_otranslator(file_path: str, source_lang: str, target_lang: str, 
                              model: str = "gemini-2.5-flash") -> Optional[str]:
    """
    Translate file using O*Translator API with formatting preservation
    """
    try:
        # Валідація мов
        if not validate_language_for_otranslator(target_lang):
            raise Exception(f"Мова {target_lang} не підтримується O*Translator API")
        
        if not validate_language_for_otranslator(source_lang):
            raise Exception(f"Мова {source_lang} не підтримується O*Translator API")
        
        headers = {
            "Authorization": f"Bearer {config.OTRANSLATOR_API_KEY}"
        }
        
        with open(file_path, "rb") as f:
            files = {
                "file": f
            }
            
            data = {
                "source_lang": source_lang.lower(),
                "target_lang": target_lang.lower(),
                "model": model  # This is the key parameter for model selection
            }
            
            logger.info(f"Sending file to O*Translator: {file_path} with model: {model}")
            
            response = requests.post(
                f"{config.OTRANSLATOR_API_URL}/translation/create",
                headers=headers,
                files=files,
                data=data,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                logger.info(f"O*Translator task created: {task_id}")
                return task_id
            else:
                logger.error(f"O*Translator API error: {response.status_code} - {response.text}")
                raise Exception(f"Помилка API: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error in O*Translator translation: {str(e)}")
        raise Exception(f"Помилка перекладу: {str(e)}")

def check_translation_status(task_id: str) -> Dict:
    """
    Check translation status
    """
    try:
        headers = {
            "Authorization": f"Bearer {config.OTRANSLATOR_API_KEY}"
        }
        
        response = requests.get(
            f"{config.OTRANSLATOR_API_URL}/translation/status/{task_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Status check failed: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Error checking translation status: {str(e)}")
        return {"status": "error", "message": str(e)}

def download_translated_file(task_id: str) -> Optional[str]:
    """
    Download translated file
    """
    try:
        headers = {
            "Authorization": f"Bearer {config.OTRANSLATOR_API_KEY}"
        }
        
        response = requests.get(
            f"{config.OTRANSLATOR_API_URL}/translation/download/{task_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            download_url = result.get("download_url")
            
            if download_url:
                # Download the actual file
                file_response = requests.get(download_url, timeout=300)
                if file_response.status_code == 200:
                    # Save file
                    import uuid
                    filename = f"temp/translated_{uuid.uuid4().hex}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(file_response.content)
                    return filename
            return None
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error downloading translated file: {str(e)}")
        return None