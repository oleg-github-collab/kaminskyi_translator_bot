from utils.otranslator_utils import translate_file_otranslator, check_translation_status, download_translated_file
from utils.file_utils import read_file_content, write_translated_file
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

async def translate_epic(file_path: str, source_lang: str, target_lang: str, 
                        file_extension: str, progress_callback=None) -> str:
    """Translate file using Kaminskyi Epic AI"""
    try:
        # Update progress
        if progress_callback:
            await progress_callback(20)
        
        # Send to O*Translator with Gemini 2.5 Flash model
        task_id = translate_file_otranslator(
            file_path, 
            source_lang, 
            target_lang, 
            model="gemini-2.5-flash"
        )
        
        if not task_id:
            raise Exception("Не вдалося створити завдання перекладу")
        
        # Update progress
        if progress_callback:
            await progress_callback(40)
        
        # Wait for completion
        translated_file_path = await wait_for_otranslator_completion(task_id, progress_callback)
        
        if not translated_file_path:
            raise Exception("Не вдалося отримати перекладений файл")
        
        # Update progress
        if progress_callback:
            await progress_callback(100)
        
        return translated_file_path
        
    except Exception as e:
        logger.error(f"Error in Epic translation: {str(e)}")
        raise Exception(f"Помилка перекладу Epic: {str(e)}")

async def wait_for_otranslator_completion(task_id: str, progress_callback=None) -> str:
    """Wait for O*Translator task completion"""
    max_attempts = 60  # 10 minutes with 10-second intervals
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Update progress periodically
            if progress_callback and attempt % 3 == 0:  # Every 30 seconds
                progress = min(90, 40 + (attempt * 50 // max_attempts))
                await progress_callback(progress)
            
            # Check task status
            status_result = check_translation_status(task_id)
            
            if status_result.get("status") == "completed":
                # Download translated file
                file_path = download_translated_file(task_id)
                return file_path
            elif status_result.get("status") == "error":
                raise Exception(f"O*Translator error: {status_result.get('message')}")
            elif status_result.get("status") == "processing":
                # Still processing, continue waiting
                pass
            else:
                logger.warning(f"Unknown status: {status_result}")
            
            # Wait before next check
            await asyncio.sleep(10)
            attempt += 1
            
        except Exception as e:
            logger.error(f"Error checking O*Translator status: {str(e)}")
            await asyncio.sleep(10)
            attempt += 1
    
    raise Exception("Час очікування перекладу вичерпано")
