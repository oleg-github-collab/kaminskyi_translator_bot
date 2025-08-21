import stripe
import config
import logging
from typing import Optional

logger = logging.getLogger(__name__)
stripe.api_key = config.STRIPE_SECRET_KEY

def calculate_price(chars: int, model: str) -> float:
    """Calculate price based on character count and model"""
    model_config = config.MODELS.get(model, config.MODELS["basic"])
    price_per_unit = model_config["price_per_unit"]
    min_price = model_config["min_price"]
    
    units = chars / config.CHARS_PER_UNIT
    price = units * price_per_unit
    return round(max(price, min_price), 2)

def create_payment_session(amount_eur: float, user_id: int, char_count: int, model: str) -> Optional[str]:
    """Create Stripe payment session optimized for Telegram"""
    try:
        model_name = config.MODELS[model]["name"]
        model_description = config.MODELS[model]["description"]
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'google_pay', 'apple_pay'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'🤖 {model_name} - Переклад тексту',
                        'description': f'{model_description}\n\n📊 Символів: {char_count:,}\n💰 Вартість: {amount_eur}€',
                        'images': ['https://via.placeholder.com/300x200/0088cc/ffffff?text=Kaminskyi+AI'],
                    },
                    'unit_amount': int(amount_eur * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{config.WEBHOOK_URL}/success?user_id={user_id}&amount={amount_eur}&model={model}&char_count={char_count}',
            cancel_url=f'{config.WEBHOOK_URL}/cancel?user_id={user_id}&reason=user_cancelled',
            expires_at=int((config.time.time() if hasattr(config, 'time') else __import__('time').time()) + 1800),  # 30 minutes
            customer_creation='if_required',
            billing_address_collection='auto',
            shipping_address_collection=None,
            phone_number_collection={'enabled': False},
            allow_promotion_codes=True,
            automatic_tax={'enabled': False},
            invoice_creation={'enabled': False},
            ui_mode='hosted',
            metadata={
                'user_id': str(user_id),
                'char_count': str(char_count),
                'amount': str(amount_eur),
                'model': model,
                'source': 'telegram_bot',
                'timestamp': str(int(__import__('time').time()))
            }
        )
        logger.info(f"Created optimized payment session for user {user_id}, amount: {amount_eur}€, model: {model}")
        return session.url
    except Exception as e:
        logger.error(f"Error creating payment session for user {user_id}: {str(e)}")
        return None

def verify_payment(session_id: str) -> dict:
    """Verify payment status with enhanced details"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Отримуємо додаткову інформацію про платіж
        payment_intent = None
        if session.payment_intent:
            payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
        
        return {
            'paid': session.payment_status == 'paid',
            'status': session.payment_status,
            'amount': session.amount_total / 100 if session.amount_total else 0,
            'currency': session.currency,
            'metadata': session.metadata,
            'customer_email': session.customer_details.email if session.customer_details else None,
            'payment_method': payment_intent.payment_method_types[0] if payment_intent and payment_intent.payment_method_types else None,
            'created': session.created,
            'expires_at': session.expires_at
        }
    except Exception as e:
        logger.error(f"Error verifying payment {session_id}: {str(e)}")
        return {'paid': False, 'metadata': {}}

def get_payment_status_message(status: str) -> str:
    """Get user-friendly payment status message"""
    status_messages = {
        'paid': '✅ Оплачено',
        'unpaid': '⏳ Очікує оплати',
        'no_payment_required': '✅ Оплата не потрібна',
        'processing': '🔄 Обробляється'
    }
    return status_messages.get(status, f'❓ Невідомий статус: {status}')

def format_payment_receipt(payment_data: dict) -> str:
    """Format payment receipt for user"""
    if not payment_data.get('paid'):
        return "❌ Платіж не знайдено або не завершено"
    
    receipt = (
        f"🧾 <b>Чек про оплату</b>\n\n"
        f"💰 Сума: {payment_data.get('amount', 0):.2f} {payment_data.get('currency', 'EUR').upper()}\n"
        f"📅 Дата: {__import__('datetime').datetime.fromtimestamp(payment_data.get('created', 0)).strftime('%d.%m.%Y %H:%M')}\n"
    )
    
    if payment_data.get('customer_email'):
        receipt += f"📧 Email: {payment_data['customer_email']}\n"
    
    if payment_data.get('payment_method'):
        receipt += f"💳 Спосіб оплати: {payment_data['payment_method']}\n"
    
    receipt += f"\n✅ Платіж успішно завершено"
    return receipt