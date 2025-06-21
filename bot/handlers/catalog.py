# bot/handlers/catalog.py
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InputMediaPhoto
from store.models import Category, SubCategory, Product, TelegramUser, CartItem
from states.order import OrderFSM
from keyboards.inline import (
    get_paginated_keyboard,
    get_product_carousel_keyboard,
    get_quantity_confirmation_keyboard
)
from loader import dp
from asgiref.sync import sync_to_async
from texts.texts import get_text
import os

LINK = os.environ.get("LINK")

@dp.callback_query(F.data == "view_catalog")
async def view_catalog(callback: CallbackQuery, state: FSMContext):
    categories = [cat async for cat in Category.objects.all()]
    
    await state.update_data(categories=[cat.id for cat in categories])

    keyboard = get_paginated_keyboard(
        items=categories,
        page=1,
        callback_prefix="category",
        item_callback_template="category_{}"
    )

    try:
        await callback.message.edit_text(get_text("choose_category"), reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("Вы уже на этой странице.")
        elif "no text in the message" in str(e):
            await callback.message.delete()
            await callback.message.answer(get_text("choose_category"), reply_markup=keyboard)
        else:
            raise e

@dp.callback_query(F.data.startswith("category_page_"))
async def paginate_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_ids = data.get("categories", [])
    categories = [await Category.objects.aget(id=i) for i in category_ids]
    page = int(callback.data.split("_")[-1])
    keyboard = get_paginated_keyboard(categories, page, "category", "category_{}")
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@dp.callback_query(F.data.startswith("category_"))
async def show_subcategories(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[-1])
    subcategories = [s async for s in SubCategory.objects.filter(category_id=category_id)]
    await state.update_data(subcategories=[s.id for s in subcategories], current_category=category_id)
    keyboard = get_paginated_keyboard(subcategories, 1, "subcategory", "subcategory_{}")
    await callback.message.edit_text(text=get_text("choose_subcategory"), reply_markup=keyboard)

@dp.callback_query(F.data.startswith("subcategory_page_"))
async def paginate_subcategories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subcat_ids = data.get("subcategories", [])
    subcategories = [await SubCategory.objects.aget(id=i) for i in subcat_ids]
    page = int(callback.data.split("_")[-1])
    keyboard = get_paginated_keyboard(subcategories, page, "subcategory", "subcategory_{}")
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@dp.callback_query(F.data.startswith("subcategory_"))
async def show_products(callback: CallbackQuery, state: FSMContext):
    subcategory_id = int(callback.data.split("_")[1])
    queryset = Product.objects.filter(subcategory_id=subcategory_id)
    products = [p async for p in queryset]

    if not products:
        return await callback.message.edit_text(get_text("products_empty"))

    await state.update_data(product_ids=[p.id for p in products], product_index=0)
    return await send_product_carousel(callback.message, products[0], 1, len(products))

@dp.callback_query(F.data.startswith("prod_page_"))
async def paginate_products(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_ids = data.get("product_ids", [])
    new_index = int(callback.data.split("_")[-1]) - 1

    if 0 <= new_index < len(product_ids):
        product = await Product.objects.aget(pk=product_ids[new_index])
        await state.update_data(product_index=new_index)
        await send_product_carousel(callback.message, product, new_index + 1, len(product_ids), edit=True)
    else:
        await callback.answer(get_text("page_not_found"), show_alert=True)

async def send_product_carousel(message, product: Product, page: int, total: int, edit: bool = True):
    text = (
        f"<b>{product.name}</b>\n"
        f"{product.description}\n"
        f"💰 Цена: {product.price}₽"
    )
    keyboard = get_product_carousel_keyboard(product.id, page, total)

    if product.photo and hasattr(product.photo, "url"):
        photo_url = f"https://{LINK}{product.photo.url}"
        media = InputMediaPhoto(media=photo_url, caption=text, parse_mode="HTML")
        if edit:
            await message.edit_media(media=media, reply_markup=keyboard)
        else:
            await message.answer_photo(photo=photo_url, caption=text, reply_markup=keyboard)
    else:
        if edit:
            await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    product = await Product.objects.aget(pk=product_id)
    await state.update_data(product_id=product_id, product_name=product.name, product_price=float(product.price))
    await state.set_state(OrderFSM.waiting_for_quantity)
    await callback.message.answer(get_text("quantity_prompt"))

@dp.message(OrderFSM.waiting_for_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 1:
        return await message.answer(get_text("invalid_quantity"))

    await state.update_data(quantity=int(message.text))
    data = await state.get_data()
    total = int(data['quantity']) * float(data['product_price'])

    text = get_text("confirm_quantity", product_name=data['product_name'], quantity=data['quantity'], total=total)
    keyboard = get_quantity_confirmation_keyboard()
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(OrderFSM.waiting_for_confirm)

@dp.callback_query(F.data == "confirm_add")
async def confirm_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user

    user_obj, _ = await TelegramUser.objects.aget_or_create(
        id=user.id,
        defaults={
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or ""
        }
    )

    cart = await sync_to_async(lambda: user_obj.cart)()
    await CartItem.objects.acreate(
        cart=cart,
        product_id=data['product_id'],
        quantity=data['quantity']
    )

    await state.clear()
    await callback.message.answer(get_text("add_success"))

@dp.callback_query(F.data == "cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(get_text("add_cancelled"))
