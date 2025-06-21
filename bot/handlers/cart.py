# bot/handlers/cart.py
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto
from store.models import TelegramUser, CartItem
from keyboards.inline import get_cart_navigation_keyboard
from loader import dp
from asgiref.sync import sync_to_async
from texts.texts import get_text
import os

LINK = os.environ.get("LINK")

CART_PAGE_SIZE = 3

async def send_cart_item(message, item, page: int, total: int, edit: bool = False):
    text = (
        f"<b>{item.product.name}</b>\n"
        f"{item.product.description}\n"
        f"\U0001F4B0 Цена: {item.product.price}₽\n"
        f"\U0001F4E6 Кол-во: {item.quantity}"
    )

    keyboard = get_cart_navigation_keyboard(page, total)

    if item.product.photo and hasattr(item.product.photo, "url"):
        photo_url = f"https://{LINK}{item.product.photo.url}"
        if edit:
            await message.edit_media(
                media=InputMediaPhoto(media=photo_url, caption=text, parse_mode="HTML"),
                reply_markup=keyboard
            )
        else:
            await message.answer_photo(photo=photo_url, caption=text, reply_markup=keyboard)
    else:
        if edit:
            await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("cart_page_"))
async def cart_pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart_items = data.get("cart_items", [])
    new_index = int(callback.data.split("_")[-1]) - 1

    if 0 <= new_index < len(cart_items):
        item_id = cart_items[new_index]
        item = await CartItem.objects.select_related("product").aget(pk=item_id)
        await state.update_data(cart_index=new_index)
        await send_cart_item(callback.message, item, new_index + 1, len(cart_items), edit=True)
    else:
        await callback.answer(get_text("page_not_found"), show_alert=True)

@dp.callback_query(F.data == "cart_remove")
async def remove_cart_item(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart_items = data.get("cart_items", [])
    cart_index = data.get("cart_index", 0)

    if cart_index >= len(cart_items):
        return await callback.message.answer(get_text("delete_error"))

    item_id = cart_items[cart_index]
    await CartItem.objects.filter(pk=item_id).adelete()

    del cart_items[cart_index]
    if not cart_items:
        await state.clear()
        return await callback.message.answer(get_text("cart_all_deleted"))

    new_index = min(cart_index, len(cart_items) - 1)
    item = await CartItem.objects.select_related("product").aget(pk=cart_items[new_index])
    await state.update_data(cart_items=cart_items, cart_index=new_index)
    await send_cart_item(callback.message, item, new_index + 1, len(cart_items))

@dp.message(F.text == "/cart")
async def show_cart_command(message: types.Message, state: FSMContext):
    await handle_cart(message, message.from_user.id, state)

@dp.callback_query(F.data == "go_to_cart")
async def show_cart_callback(callback: CallbackQuery, state: FSMContext):
    await handle_cart(callback.message, callback.from_user.id, state)

async def handle_cart(message: types.Message, user_id: int, state: FSMContext):
    try:
        tg_user = await TelegramUser.objects.aget(pk=user_id)
        cart = await sync_to_async(lambda: tg_user.cart)()
        cart_items = await sync_to_async(lambda: list(cart.items.select_related("product").all()))()
    except Exception:
        return await message.answer(get_text("cart_load_failed"))

    if not cart_items:
        return await message.answer(get_text("cart_empty"))

    await state.update_data(cart_items=[item.id for item in cart_items], cart_index=0)
    current_item = cart_items[0]
    return await send_cart_item(message, current_item, 1, len(cart_items))
