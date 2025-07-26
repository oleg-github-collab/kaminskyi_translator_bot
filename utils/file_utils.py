import os
import logging
from docx import Document
import pdfplumber

logger = logging.getLogger(__name__)

def count_chars_in_file(file_path: str) -> int:
    """ПОВНА, ПЕРЕВІРЕНА функція підрахунку символів"""
    try:
        logger.info(f"Starting character count for file: {file_path}")
        
        # Перевірка існування файлу
        if not file_path or not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return 0
            
        # Перевірка чи файл не порожній
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.warning(f"File is empty: {file_path}")
            return 0
            
        logger.info(f"File exists, size: {file_size} bytes")
        
        # Отримання розширення файлу
        _, ext = os.path.splitext(file_path)
        if not ext:
            logger.error(f"No extension found for file: {file_path}")
            return 0
            
        ext = ext.lower()
        logger.info(f"File extension: {ext}")
        
        char_count = 0
        
        if ext == '.txt':
            char_count = _count_txt_file(file_path)
        elif ext == '.docx':
            char_count = _count_docx_file(file_path)
        elif ext == '.pdf':
            char_count = _count_pdf_file(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return 0
            
        logger.info(f"Final character count for {file_path}: {char_count}")
        return char_count if char_count is not None else 0
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in count_chars_in_file for {file_path}: {str(e)}", exc_info=True)
        return 0

def _count_txt_file(file_path: str) -> int:
    """Підрахунок символів у TXT файлі"""
    try:
        logger.info(f"Counting TXT file: {file_path}")
        
        encodings = ['utf-8', 'windows-1251', 'cp1251', 'latin1', 'utf-16']
        last_error = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    char_count = len(content)
                    if char_count > 0:
                        logger.info(f"Successfully read TXT file {file_path} with {encoding}: {char_count} chars")
                        return char_count
                    else:
                        logger.debug(f"TXT file {file_path} with {encoding} is empty")
            except Exception as e:
                last_error = e
                logger.debug(f"Failed to read TXT with {encoding}: {str(e)}")
                continue
                
        logger.warning(f"Could not read meaningful content from TXT file: {file_path}, last error: {last_error}")
        return 0
        
    except Exception as e:
        logger.error(f"Error in _count_txt_file for {file_path}: {str(e)}")
        return 0

def _count_docx_file(file_path: str) -> int:
    """Підрахунок символів у DOCX файлі"""
    try:
        logger.info(f"Counting DOCX file: {file_path}")
        
        doc = Document(file_path)
        total_chars = 0
        paragraph_count = 0
        
        for paragraph in doc.paragraphs:
            if paragraph.text and paragraph.text.strip():
                total_chars += len(paragraph.text)
                paragraph_count += 1
                
        logger.info(f"DOCX file {file_path}: {total_chars} chars in {paragraph_count} paragraphs")
        return total_chars
        
    except Exception as e:
        logger.error(f"Error counting DOCX file {file_path}: {str(e)}")
        return 0

def _count_pdf_file(file_path: str) -> int:
    """Підрахунок символів у PDF файлі"""
    try:
        logger.info(f"Counting PDF file: {file_path}")
        
        total_chars = 0
        page_count = 0
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        page_chars = len(text)
                        total_chars += page_chars
                        page_count += 1
                        logger.debug(f"Page {page_num} extracted {page_chars} chars")
                    else:
                        logger.debug(f"Page {page_num} is empty")
                except Exception as page_error:
                    logger.warning(f"Error extracting text from page {page_num} in {file_path}: {str(page_error)}")
                    continue
                    
        logger.info(f"PDF file {file_path}: {total_chars} chars in {page_count} pages")
        return total_chars
        
    except Exception as e:
        logger.error(f"Error counting PDF file {file_path}: {str(e)}")
        return 0

def read_file_content(file_path: str) -> str:
    """Читання вмісту файлу"""
    try:
        if not os.path.exists(file_path):
            return ""
            
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        content = ""
        
        if ext == '.txt':
            encodings = ['utf-8', 'windows-1251', 'cp1251', 'latin1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                        if content.strip():
                            break
                except:
                    continue
                    
        elif ext == '.docx':
            try:
                doc = Document(file_path)
                content = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
            except:
                pass
                
        elif ext == '.pdf':
            try:
                text = ''
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + '\n'
                        except:
                            continue
                content = text.strip()
            except:
                pass
                
        return content
        
    except:
        return ""

def write_translated_file(file_path: str, translated_text: str, original_ext: str) -> str:
    """Створення перекладеного файлу"""
    try:
        if not translated_text or not translated_text.strip():
            raise Exception("Перекладений текст порожній")
            
        base_name = os.path.splitext(file_path)[0]
        new_file_path = f"{base_name}_translated{original_ext}"
        
        if original_ext == '.txt':
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
                
        elif original_ext == '.docx':
            doc = Document()
            for line in translated_text.split('\n'):
                if line.strip():
                    doc.add_paragraph(line)
            doc.save(new_file_path)
                
        else:
            txt_path = new_file_path + '.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            return txt_path
            
        return new_file_path
        
    except Exception as e:
        raise Exception(f"Помилка створення файлу: {str(e)}")

def cleanup_temp_file(file_path: str):
    """Очищення тимчасових файлів"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except:
        return False