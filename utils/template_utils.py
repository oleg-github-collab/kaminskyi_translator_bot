import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TemplateRenderer:
    """Клас для роботи з HTML шаблонами"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.template_cache = {}
    
    def load_template(self, template_name: str) -> Optional[str]:
        """Завантаження HTML шаблону з кешуванням"""
        try:
            # Перевіряємо кеш
            if template_name in self.template_cache:
                return self.template_cache[template_name]
            
            template_path = os.path.join(self.templates_dir, template_name)
            
            if not os.path.exists(template_path):
                logger.error(f"Template not found: {template_path}")
                return None
            
            with open(template_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                # Кешуємо шаблон
                self.template_cache[template_name] = template_content
                return template_content
                
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            return None
    
    def render_template(self, template_name: str, context: Dict = None) -> Optional[str]:
        """Рендеринг шаблону з підстановкою змінних"""
        try:
            template = self.load_template(template_name)
            if not template:
                return None
            
            if context:
                # Простий рендеринг через format
                template = template.format(**context)
            
            return template
            
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            return None
    
    def clear_cache(self):
        """Очищення кешу шаблонів"""
        self.template_cache.clear()
        logger.info("Template cache cleared")

# Глобальний екземпляр рендерера
template_renderer = TemplateRenderer()

def render_success_page(user_id: int = None, amount: float = None, 
                       model: str = None, char_count: int = None) -> str:
    """Рендеринг сторінки успішної оплати"""
    context = {
        'user_id': user_id or '',
        'amount': f'{amount:.2f}' if amount else '',
        'model': model or '',
        'char_count': f'{char_count:,}' if char_count else ''
    }
    
    template = template_renderer.render_template('payment_success.html', context)
    
    if not template:
        # Fallback на базову HTML сторінку
        return get_fallback_success_html()
    
    return template

def render_cancel_page(user_id: int = None, reason: str = None) -> str:
    """Рендеринг сторінки скасування оплати"""
    context = {
        'user_id': user_id or '',
        'reason': reason or 'cancelled'
    }
    
    template = template_renderer.render_template('payment_cancel.html', context)
    
    if not template:
        return get_fallback_cancel_html()
    
    return template

def render_info_page() -> str:
    """Рендеринг інформаційної сторінки"""
    template = template_renderer.render_template('payment_info.html')
    
    if not template:
        return get_fallback_info_html()
    
    return template

def get_fallback_success_html() -> str:
    """Запасна HTML сторінка для успішної оплати"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Оплата успішна</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { background: white; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; }
            .success { color: #28a745; font-size: 48px; margin-bottom: 20px; }
            h1 { color: #333; margin-bottom: 20px; }
            p { color: #666; line-height: 1.6; }
            .bot-link { display: inline-block; background: #0088cc; color: white; padding: 12px 24px; 
                       text-decoration: none; border-radius: 5px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">✅</div>
            <h1>Оплата успішна!</h1>
            <p>Дякуємо за оплату. Поверніться до бота для продовження роботи.</p>
            <a href="https://t.me/KaminskyiAIBot" class="bot-link">Повернутися до бота</a>
        </div>
        <script>setTimeout(() => window.close(), 5000);</script>
    </body>
    </html>
    """

def get_fallback_cancel_html() -> str:
    """Запасна HTML сторінка для скасування оплати"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Оплата скасована</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { background: white; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; }
            .cancel { color: #dc3545; font-size: 48px; margin-bottom: 20px; }
            h1 { color: #333; margin-bottom: 20px; }
            p { color: #666; line-height: 1.6; }
            .bot-link { display: inline-block; background: #0088cc; color: white; padding: 12px 24px; 
                       text-decoration: none; border-radius: 5px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="cancel">❌</div>
            <h1>Оплата скасована</h1>
            <p>Не проблема! Ви можете повернутися до бота та спробувати ще раз.</p>
            <a href="https://t.me/KaminskyiAIBot" class="bot-link">Повернутися до бота</a>
        </div>
        <script>setTimeout(() => window.close(), 3000);</script>
    </body>
    </html>
    """

def get_fallback_info_html() -> str:
    """Запасна інформаційна HTML сторінка"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kaminskyi AI - Інформація</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 40px; border-radius: 10px; max-width: 800px; margin: 0 auto; }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .pricing { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center; }
            .price { font-size: 24px; color: #28a745; font-weight: bold; margin: 10px 0; }
            .bot-link { display: inline-block; background: #0088cc; color: white; padding: 15px 30px; 
                       text-decoration: none; border-radius: 25px; margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Kaminskyi AI Translator</h1>
            <div class="pricing">
                <div class="card">
                    <h3>⚡ Basic</h3>
                    <div class="price">0.65€</div>
                    <p>Швидкий переклад через DeepL</p>
                </div>
                <div class="card">
                    <h3>🎯 Epic</h3>
                    <div class="price">0.95€</div>
                    <p>Найкраща якість через Gemini 2.5</p>
                </div>
            </div>
            <div style="text-align: center;">
                <a href="https://t.me/KaminskyiAIBot" class="bot-link">Розпочати в Telegram</a>
            </div>
        </div>
    </body>
    </html>
    """

def validate_template_files() -> Dict[str, bool]:
    """Перевірка наявності всіх необхідних шаблонів"""
    templates = {
        'payment_success.html': False,
        'payment_cancel.html': False,
        'payment_info.html': False
    }
    
    templates_dir = "templates"
    
    for template_name in templates.keys():
        template_path = os.path.join(templates_dir, template_name)
        templates[template_name] = os.path.exists(template_path)
    
    return templates

def setup_templates_directory():
    """Створення директорії для шаблонів якщо не існує"""
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        logger.info(f"Created templates directory: {templates_dir}")
    return templates_dir