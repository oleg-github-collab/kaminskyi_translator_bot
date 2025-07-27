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

def create_payment_session(
    amount_eur: float, user_id: int, char_count: int, model: str
) -> Optional[tuple]:
    """Create Stripe payment session"""
    try:
        model_name = config.MODELS[model]["name"]
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'{model_name} Translation',
                        'description': f'Translation of {char_count:,} characters using {model_name}',
                    },
                    'unit_amount': int(amount_eur * 100),  # In cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{config.WEBHOOK_URL}/success?user_id={user_id}',
            cancel_url=f'{config.WEBHOOK_URL}/cancel?user_id={user_id}',
            metadata={
                'user_id': str(user_id),
                'char_count': str(char_count),
                'amount': str(amount_eur),
                'model': model
            }
        )
        logger.info(
            f"Created payment session for user {user_id}, amount: {amount_eur}€, model: {model}"
        )
        return session.url, session.id
    except Exception as e:
        logger.error(f"Error creating payment session for user {user_id}: {str(e)}")
        return None

def verify_payment(session_id: str) -> dict:
    """Verify payment status"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'paid': session.payment_status == 'paid',
            'metadata': session.metadata
        }
    except Exception as e:
        logger.error(f"Error verifying payment {session_id}: {str(e)}")
        return {'paid': False, 'metadata': {}}