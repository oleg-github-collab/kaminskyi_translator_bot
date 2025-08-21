# 💳 Налаштування платіжної системи Stripe

## 🚀 Основні покращення

### ✅ Що реалізовано:

1. **Повноцінна Stripe інтеграція**
   - Реальні платіжні сесії замість заглушок
   - Підтримка карт, Google Pay, Apple Pay
   - Автоматичне створення чеків

2. **Оптимізований UI для Telegram**
   - Платіжне вікно відкривається прямо в Telegram через веб-переглядач
   - Красиві HTML сторінки успіху/скасування
   - Автоматичне закриття вікон

3. **Покращений користувацький досвід**
   - Детальна інформація про платежі
   - Інтерактивні клавіатури з контекстною інформацією
   - Система підтримки з контактними даними
   - Автоматичні повідомлення про статус оплати

4. **Надійна обробка помилок**
   - Валідація всіх даних
   - Детальне логування платіжних операцій
   - Graceful error handling з користувацькими повідомленнями
   - Окремі логи для платежів

5. **Webhook інтеграція**
   - Автоматичне підтвердження платежів
   - Обробка expired сесій
   - Відправка повідомлень користувачам

## 🔧 Необхідне налаштування

### 1. Stripe налаштування

```bash
# У .env файлі додайте:
STRIPE_SECRET_KEY=sk_test_...  # Ваш секретний ключ Stripe
STRIPE_WEBHOOK_SECRET=whsec_...  # Webhook секрет
WEBHOOK_URL=https://yourdomain.com  # Ваш домен
```

### 2. Stripe Dashboard

1. Увійдіть в [Stripe Dashboard](https://dashboard.stripe.com/)
2. Перейдіть до **Developers > Webhooks**
3. Створіть новий endpoint: `https://yourdomain.com/webhook/stripe`
4. Виберіть події:
   - `checkout.session.completed`
   - `checkout.session.expired`
5. Скопіюйте webhook secret у `.env`

### 3. Домен та SSL

- Обов'язково використовуйте HTTPS (SSL сертифікат)
- Налаштуйте правильні success/cancel URL
- Перевірте доступність вашого домену

## 🎯 Ключові файли

### `handlers/payment.py`
- **`process_payment()`** - головна функція обробки платежів
- **`payment_help()`** - система підтримки
- **`start_translation()`** - автоматичний початок після оплати
- **`payment_details()`** - детальна інформація
- **`contact_support()`** - контакти підтримки

### `utils/payment_utils.py`
- **`create_payment_session()`** - створення Stripe сесій
- **`verify_payment()`** - перевірка статусу платежу
- **`calculate_price()`** - розрахунок вартості
- **`format_payment_receipt()`** - форматування чеків

### `handlers/webhook.py`
- **`stripe_webhook()`** - обробка Stripe подій
- **`success_page()`** - HTML сторінка успішної оплати
- **`cancel_page()`** - HTML сторінка скасованої оплати
- **`info_page()`** - інформаційна сторінка з цінами

### `utils/error_handler.py`
- **`@payment_error_handler`** - декоратор для обробки помилок
- **`validate_payment_data()`** - валідація платіжних даних
- **`log_payment_action()`** - логування дій
- **`PaymentValidator`** - клас валідації

### `utils/template_utils.py`
- **`TemplateRenderer`** - рендеринг HTML шаблонів
- **`render_success_page()`** - генерація сторінки успіху
- **`render_cancel_page()`** - генерація сторінки скасування
- **`validate_template_files()`** - перевірка шаблонів

### `templates/` директорія
- **`payment_success.html`** - красива сторінка успішної оплати
- **`payment_cancel.html`** - стилізована сторінка скасування
- **`payment_info.html`** - інформаційна сторінка з цінами

## 📱 Користувацький потік

1. **Завантаження файлу** → Аналіз тексту
2. **Вибір моделі** → Розрахунок ціни
3. **Підтвердження** → Деталі оплати
4. **Оплата** → Stripe вікно (в Telegram)
5. **Підтвердження** → Автоматичний початок перекладу

## 🔍 Особливості

### Stripe для Telegram
- Використовуємо `ui_mode: 'hosted'` для кращої інтеграції
- Експірація сесій через 30 хвилин
- Підтримка промокодів
- Автоматичне визначення адреси

### HTML Шаблони
- Красиві responsive сторінки успіху/скасування
- Автоматичне закриття вікон через N секунд
- Інформаційна сторінка з цінами та деталями
- Fallback на базовий HTML у разі помилок
- Кешування шаблонів для швидкості

### Безпека
- Всі дані валідуються перед обробкою
- Логування всіх платіжних операцій
- Санітизація користувацького вводу
- Захищені webhook'и з підписами

### Логування
```
logs/
├── bot.log          # Загальні логи
└── payment.log      # Платіжні операції
```

## 🧪 Тестування

1. **Тест Stripe**:
   ```
   Використовуйте тестові картки:
   4242 4242 4242 4242 (Visa)
   5555 5555 5555 4444 (Mastercard)
   ```

2. **Тест webhook'ів**:
   ```bash
   # Використовуйте Stripe CLI
   stripe listen --forward-to localhost:8000/webhook/stripe
   ```

3. **Локальне тестування**:
   ```bash
   # Запустіть ngrok для HTTPS
   ngrok http 8000
   ```

4. **Тест HTML шаблонів**:
   ```bash
   # Перевірте наявність шаблонів
   python3 -c "from utils.template_utils import validate_template_files; print(validate_template_files())"
   
   # Доступ до сторінок:
   # http://localhost:8000/success?user_id=123&amount=2.50&model=epic&char_count=5000
   # http://localhost:8000/cancel?user_id=123&reason=user_cancelled
   # http://localhost:8000/info
   ```

## 📊 Моніторинг

### Метрики для відстеження:
- Успішність платежів
- Час обробки
- Частота помилок
- Конверсія по моделях

### Логи платежів:
```python
# Приклад лог-запису
{
    "action": "payment_completed",
    "user_id": 12345,
    "timestamp": 1703087234,
    "details": {
        "amount": 2.50,
        "model": "epic",
        "char_count": 5000
    }
}
```

## 🚨 Важливі нотатки

1. **Ніколи не комітьте** реальні API ключі
2. **Завжди використовуйте** HTTPS у продакшені
3. **Регулярно перевіряйте** webhook'и в Stripe Dashboard
4. **Моніторте** логи платежів для виявлення проблем
5. **Тестуйте** на staging перед деплоєм

## 📞 Підтримка

- **Email**: support@kaminskyi.ai
- **Telegram**: @KaminskyiSupport
- **Документація**: [Stripe Docs](https://stripe.com/docs)

---
**Створено з ❤️ для найкращого досвіду користувачів Telegram**