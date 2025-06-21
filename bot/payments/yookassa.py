import uuid
import os
from yookassa import Configuration, Payment

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")
RETURN_URL = os.getenv("RETURN_URL")

def create_yookassa_payment(order_id: int, amount: float):
    
    payment = Payment.create({
        "amount": {
            "value": f"{amount:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": RETURN_URL
        },
        "capture": True,
        "description": f"Оплата заказа №{order_id}",
        "metadata": {
            "order_id": order_id
        }
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url
