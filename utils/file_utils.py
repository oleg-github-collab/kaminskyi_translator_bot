import os
import logging
from docx import Document
import pdfplumber
from PyPDF2 import PdfReader
import tempfile

logger = logging.getLogger(__name__)

def count_chars_in_file(file_path: str) -> int:
    try:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.read())
        elif ext == '.docx':
            doc = Document(file_path)
            return sum(len(paragraph.text) for paragraph in doc.paragraphs)
        elif ext == '.pdf':
            total_chars = 0
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        total_chars += len(text)
            return total_chars
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return 0
            
    except Exception as e:
        logger.error(f"Error counting chars in {file_path}: {str(e)}")
        return 0

def read_file_content(file_path: str) -> str:
    try:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.docx':
            doc = Document(file_path)
            return '\n'.join(paragraph.text for paragraph in doc.paragraphs)
        elif ext == '.pdf':
            text = ''
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
            return text.strip()
        else:
            logger.warning(f"Unsupported file type for reading: {ext}")
            return ""
            
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return ""

def write_translated_file(file_path: str, translated_text: str, original_ext: str) -> str:
    try:
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
        elif original_ext == '.pdf':
            # For PDF, save as TXT since we can't preserve complex formatting
            txt_path = new_file_path.replace('.pdf', '.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            return txt_path
        else:
            # Default to TXT
            txt_path = new_file_path + '.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            return txt_path
            
        return new_file_path
        
    except Exception as e:
        logger.error(f"Error writing translated file {file_path}: {str(e)}")
        raise Exception(f"Помилка створення файлу: {str(e)}")

def cleanup_temp_file(file_path: str):
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {str(e)}")