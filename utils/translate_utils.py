import requests
import time
import config
import logging
from typing import Optional, Dict
import os
import asyncio

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


async def translate_document_deepl(
    file_path: str,
    target_lang: str,
    source_lang: str = None,
    progress_callback=None,
) -> str:
    """Translate document using DeepL document translation API"""
    if not config.DEEPL_API_KEY:
        raise Exception("DEEPL_API_KEY не налаштовано")

    try:
        params = {"auth_key": config.DEEPL_API_KEY}
        data = {"target_lang": target_lang.upper()}
        if source_lang:
            data["source_lang"] = source_lang.upper()

        with open(file_path, "rb") as f:
            files = {"file": f}
            resp = requests.post(
                "https://api-free.deepl.com/v2/document",
                params=params,
                data=data,
                files=files,
                timeout=300,
            )

        if resp.status_code != 200:
            raise Exception(
                f"DeepL document upload failed: {resp.status_code} {resp.text}"
            )

        info = resp.json()
        document_id = info.get("document_id")
        document_key = info.get("document_key")
        if not document_id or not document_key:
            raise Exception("Помилкова відповідь DeepL")

        status_url = f"https://api-free.deepl.com/v2/document/{document_id}"
        params.update({"document_key": document_key})

        for i in range(60):
            status = requests.get(status_url, params=params, timeout=30)
            if status.status_code != 200:
                raise Exception(
                    f"DeepL status error: {status.status_code} {status.text}"
                )
            result = status.json()
            if result.get("status") == "done":
                download = requests.get(
                    f"{status_url}/result",
                    params=params,
                    timeout=300,
                )
                if download.status_code == 200:
                    out_path = os.path.join(
                        config.TEMP_DIR,
                        f"deepl_{int(time.time())}_{os.path.basename(file_path)}",
                    )
                    with open(out_path, "wb") as out:
                        out.write(download.content)
                    if progress_callback:
                        await progress_callback(100)
                    return out_path
                raise Exception(
                    f"DeepL download failed: {download.status_code}"
                )
            elif result.get("status") == "error":
                raise Exception(result.get("message", "Unknown error"))

            if progress_callback:
                percent = min(90, 20 + i)
                try:
                    await progress_callback(percent)
                except Exception:
                    pass
            await asyncio.sleep(5)

        raise Exception("Час очікування DeepL документу вичерпано")
    except Exception as e:
        logger.error(f"DeepL document translation error: {str(e)}")
        raise
