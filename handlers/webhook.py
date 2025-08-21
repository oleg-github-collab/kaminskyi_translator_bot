from aiohttp import web
import stripe
import config
import logging
import asyncio
import json
from utils.logger import log_user_action
from utils.template_utils import render_success_page, render_cancel_page, render_info_page
from aiogram import Bot

logger = logging.getLogger(__name__)
bot = Bot(token=config.BOT_TOKEN)

async def stripe_webhook(request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.read()
        sig_header = request.headers.get('Stripe-Signature')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, config.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return web.Response(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return web.Response(status=400)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = int(session['metadata'].get('user_id'))
            amount = session['amount_total'] / 100
            char_count = session['metadata'].get('char_count')
            model = session['metadata'].get('model')
            
            logger.info(f"Payment completed for user {user_id}, amount: {amount}€")
            log_user_action(user_id, "payment_completed", f"amount: {amount}€, chars: {char_count}, model: {model}")
            
            # Повідомляємо користувача про успішну оплату
            try:
                success_message = (
                    f"✅ <b>Оплата успішна!</b>\n\n"
                    f"💰 Сума: {amount}€\n"
                    f"📄 Символів: {char_count}\n"
                    f"🎯 Модель: {config.MODELS.get(model, {}).get('name', model)}\n\n"
                    f"🔄 Починаємо переклад вашого файлу...\n"
                    f"⏱️ Орієнтовний час: 30-60 секунд"
                )
                
                await bot.send_message(
                    chat_id=user_id,
                    text=success_message,
                    parse_mode="HTML"
                )
                
                # Додаємо кнопку для продовження перекладу
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("🚀 Почати переклад", callback_data="start_translation"))
                
                await bot.send_message(
                    chat_id=user_id,
                    text="🚀 Готові до перекладу! Натисніть кнопку нижче:",
                    reply_markup=keyboard
                )
                
            except Exception as e:
                logger.error(f"Error sending payment confirmation to user {user_id}: {str(e)}")
        
        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            user_id = int(session['metadata'].get('user_id'))
            logger.info(f"Payment session expired for user {user_id}")
            
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text="⏰ <b>Час сесії оплати минув</b>\n\nВи можете створити новий платіж або завантажити інший файл.",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Error sending payment expiry notification to user {user_id}: {str(e)}")
        
        return web.Response(status=200)
        
    except Exception as e:
        logger.error(f"Error in stripe webhook: {str(e)}")
        return web.Response(status=500)

async def success_page(request):
    """Handle successful payment redirect with template rendering"""
    user_id = request.query.get('user_id')
    amount = request.query.get('amount')
    model = request.query.get('model')
    char_count = request.query.get('char_count')
    
    if user_id:
        log_user_action(user_id, "payment_redirect_success", {
            'amount': amount,
            'model': model,
            'char_count': char_count
        })
    
    # Рендеримо HTML з шаблону
    success_html = render_success_page(
        user_id=int(user_id) if user_id and user_id.isdigit() else None,
        amount=float(amount) if amount else None,
        model=model,
        char_count=int(char_count) if char_count and char_count.isdigit() else None
    )
    
    return web.Response(text=success_html, content_type='text/html; charset=utf-8')

async def cancel_page(request):
    """Handle cancelled payment redirect with template rendering"""
    user_id = request.query.get('user_id')
    reason = request.query.get('reason', 'user_cancelled')
    
    if user_id:
        log_user_action(user_id, "payment_redirect_cancelled", {'reason': reason})
    
    # Рендеримо HTML з шаблону
    cancel_html = render_cancel_page(
        user_id=int(user_id) if user_id and user_id.isdigit() else None,
        reason=reason
    )
    
    return web.Response(text=cancel_html, content_type='text/html; charset=utf-8')

async def info_page(request):
    """Handle payment info page"""
    info_html = render_info_page()
    return web.Response(text=info_html, content_type='text/html; charset=utf-8')

def setup_webhooks(app):
    """Setup webhook routes with additional pages"""
    app.router.add_post('/webhook/stripe', stripe_webhook)
    app.router.add_get('/success', success_page)
    app.router.add_get('/cancel', cancel_page)
    app.router.add_get('/info', info_page)
    app.router.add_get('/pricing', info_page)  # Альяс для інфо сторінки