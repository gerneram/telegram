# handlers/payment.py
from aiogram import F, types
from loader import dp
from payments.yookassa import create_yookassa_payment
from keyboards.inline import get_payment_keyboard
from store.models import Order, OrderItem

@dp.callback_query(F.data.startswith("pay_order_"))
async def start_payment(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[-1])
    order = await Order.objects.aget(pk=order_id)
    items = [item async for item in OrderItem.objects.select_related("product").filter(order=order)]
    amount = sum(item.quantity * float(item.product.price) for item in items)

    try:
        pay_url = create_yookassa_payment(order_id, amount)
        keyboard = get_payment_keyboard(order_id, pay_url)
        await callback.message.edit_text(f"Перейдите по ссылке для оплаты заказа №{order_id}", reply_markup=keyboard)
    except Exception as e:
        await callback.message.answer("Ошибка при создании платежа")
        raise e
