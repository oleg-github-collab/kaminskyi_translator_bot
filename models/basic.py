from utils.translate_utils import translate_text_deepl, translate_document_deepl
from utils.file_utils import read_file_content, write_translated_file
import logging
import asyncio

logger = logging.getLogger(__name__)

async def translate_basic(file_path: str, source_lang: str, target_lang: str, 
                         file_extension: str, progress_callback=None) -> str:
    """Translate file using Kaminskyi Basic (DeepL)"""
    try:
        if file_extension == '.txt':
            # Read file content
            content = read_file_content(file_path)
            if not content:
                raise Exception("Не вдалося прочитати вміст файлу")

            if progress_callback:
                await progress_callback(30)

            translated_text = translate_text_deepl(
                content, target_lang, source_lang
            )

            if progress_callback:
                await progress_callback(80)

            translated_file_path = write_translated_file(
                file_path, translated_text, file_extension
            )

            if progress_callback:
                await progress_callback(100)
        else:
            if progress_callback:
                await progress_callback(20)
            translated_file_path = await translate_document_deepl(
                file_path, target_lang, source_lang, progress_callback
            )

        return translated_file_path
        
    except Exception as e:
        logger.error(f"Error in Basic translation: {str(e)}")
        raise Exception(f"Помилка перекладу Basic: {str(e)}")
