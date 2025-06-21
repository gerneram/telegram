import os
from payments.yookassa import create_yookassa_payment
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from store.models import TelegramUser, Order, OrderItem
from states.order import OrderFSM
from keyboards.inline import get_phone_request_keyboard, get_payment_keyboard
from loader import dp
from asgiref.sync import sync_to_async
from texts.texts import get_text
import openpyxl
from pathlib import Path

@dp.callback_query(F.data == "place_order")
async def place_order(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    tg_user = await TelegramUser.objects.aget(pk=user.id)
    cart = await sync_to_async(lambda: tg_user.cart)()
    cart_items = await sync_to_async(lambda: list(cart.items.select_related("product").all()))()

    if not cart_items:
        return await callback.message.answer(get_text("cart_empty"))

    await state.update_data(cart_items=cart_items)
    await state.set_state(OrderFSM.waiting_for_name)
    await callback.message.answer(get_text("enter_name"))

@dp.message(OrderFSM.waiting_for_name)
async def get_order_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderFSM.waiting_for_address)
    await message.answer(get_text("enter_address"))

@dp.message(OrderFSM.waiting_for_address)
async def get_order_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderFSM.waiting_for_phone)
    await message.answer(get_text("share_phone"), reply_markup=get_phone_request_keyboard())

@dp.message(OrderFSM.waiting_for_phone)
async def get_order_phone(message: types.Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        return await message.answer("Пожалуйста, нажмите кнопку, чтобы отправить свой номер телефона.")

    await message.answer(get_text("phone_received"), reply_markup=ReplyKeyboardRemove())

    data = await state.get_data()
    user = message.from_user
    phone = message.contact.phone_number
    tg_user = await TelegramUser.objects.aget(id=user.id)

    order = await Order.objects.acreate(
        user=tg_user,
        name=data["name"],
        address=data["address"],
        phone=phone,
    )

    total = 0
    product_list = []
    for item in data["cart_items"]:
        await OrderItem.objects.acreate(
            order=order,
            product=item.product,
            quantity=item.quantity
        )
        total += item.quantity * float(item.product.price)
        product_list.append(f"ID товара - {item.product.id} количество:{item.quantity},")

    await sync_to_async(lambda: tg_user.cart.items.all().delete())()
    await state.clear()

    payment_url = create_yookassa_payment(order.id, total)
    
    await message.answer(
        get_text("order_success", total=total),
        reply_markup=get_payment_keyboard(order.id)
    )
    
    await message.answer(
    f"💳 Для оплаты перейдите по ссылке:\n{payment_url}"
    )

@dp.callback_query(F.data.startswith("pay_"))
async def confirm_payment(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[-1])
    order = await Order.objects.select_related("user").aget(pk=order_id)
    items = [item async for item in OrderItem.objects.select_related("product").filter(order=order)]
    total = sum(item.quantity * float(item.product.price) for item in items)
    product_list = [f"ID товара - {item.product.id} количество:{item.quantity}" for item in items]

    await Order.objects.filter(pk=order_id).aupdate(is_paid=True)

    excel_path = Path("orders.xlsx")
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    if not excel_path.exists():
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Order ID", "Username", "Name", "Phone", "Address", "Total", "Products"])
        wb.save(excel_path)

    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    ws.append([
        order.id,
        order.user.username,
        order.name,
        order.phone,
        order.address,
        total,
        "; ".join(product_list)
    ])
    wb.save(excel_path)

    await callback.message.edit_text(get_text("order_paid"))
