from aiohttp import web
import stripe
import config
import logging
from utils.logger import log_user_action

logger = logging.getLogger(__name__)

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
            user_id = session['metadata'].get('user_id')
            logger.info(f"Payment completed for user {user_id}")
            log_user_action(user_id, "payment_completed", f"amount: {session['amount_total']/100}€")
        
        return web.Response(status=200)
        
    except Exception as e:
        logger.error(f"Error in stripe webhook: {str(e)}")
        return web.Response(status=500)

async def success_page(request):
    """Handle successful payment redirect"""
    user_id = request.query.get('user_id')
    if user_id:
        log_user_action(user_id, "payment_redirect_success")
    return web.Response(text="Payment successful! You can close this window and return to the bot.")

async def cancel_page(request):
    """Handle cancelled payment redirect"""
    user_id = request.query.get('user_id')
    if user_id:
        log_user_action(user_id, "payment_redirect_cancelled")
    return web.Response(text="Payment cancelled. You can close this window and return to the bot.")

def setup_webhooks(app):
    """Setup webhook routes"""
    app.router.add_post('/webhook/stripe', stripe_webhook)
    app.router.add_get('/success', success_page)
    app.router.add_get('/cancel', cancel_page)