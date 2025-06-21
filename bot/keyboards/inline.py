from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Callable
from math import ceil


def make_inline_keyboard(rows: List[List[dict]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(**button) for button in row]
            for row in rows
        ]
    )

def make_reply_keyboard(rows: List[List[dict]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(**button) for button in row]
            for row in rows
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_start_keyboard() -> InlineKeyboardMarkup:
    return make_inline_keyboard([
        [{"text": "📦 Каталог", "callback_data": "view_catalog"}],
        [{"text": "❓ FAQ", "callback_data": "view_faq"}],
        [{"text": "🛒 Корзина", "callback_data": "go_to_cart"}]
    ])

def get_list_keyboard(items: list, prefix: str) -> InlineKeyboardMarkup:
    return make_inline_keyboard([
        [{"text": getattr(item, "name", getattr(item, "question", str(item))), "callback_data": f"{prefix}_{item.id}"}]
        for item in items
    ])

def get_faq_keyboard(faqs: list) -> InlineKeyboardMarkup:
    return get_list_keyboard(faqs, "faq")

def get_categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    rows = [[{"text": cat.name, "callback_data": f"category_{cat.id}"}] for cat in categories]
    rows.append([{"text": "🔙 Назад", "callback_data": "go_to_start"}])
    return make_inline_keyboard(rows)

def get_subcategories_keyboard(subcategories: list) -> InlineKeyboardMarkup:
    rows = [[{"text": sub.name, "callback_data": f"subcategory_{sub.id}"}] for sub in subcategories]
    rows.append([{"text": "🔙 Назад", "callback_data": "go_to_start"}])
    return make_inline_keyboard(rows)

def get_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return make_inline_keyboard([
        [{"text": "➕ Добавить", "callback_data": f"add_{product_id}"}]
    ])

def get_quantity_confirmation_keyboard() -> InlineKeyboardMarkup:
    return make_inline_keyboard([
        [
            {"text": "✅ Подтвердить", "callback_data": "confirm_add"},
            {"text": "❌ Отменить", "callback_data": "cancel_add"}
        ]
    ])

def get_cart_keyboard(with_confirm: bool = False) -> InlineKeyboardMarkup:
    buttons = [[{"text": "🗑 Удалить товар", "callback_data": "remove_from_cart"}]]
    if with_confirm:
        buttons.append([{ "text": "📦 Оформить заказ", "callback_data": "place_order" }])
    return make_inline_keyboard(buttons)

def get_cart_navigation_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    nav_row = []
    if current_page > 1:
        nav_row.append({"text": "⬅️ Назад", "callback_data": f"cart_page_{current_page - 1}"})
    if current_page < total_pages:
        nav_row.append({"text": "➡️ Далее", "callback_data": f"cart_page_{current_page + 1}"})

    buttons = []
    if nav_row:
        buttons.append(nav_row)

    buttons.append([
        {"text": "🗑 Удалить товар", "callback_data": "cart_remove"},
        {"text": "🔙 Назад", "callback_data": "view_catalog"}
    ])
    buttons.append([
        {"text": "🛍️🔥Оформить заказ", "callback_data": "place_order"}
    ])
    return make_inline_keyboard(buttons)

def get_product_carousel_keyboard(product_id: int, current: int, total: int) -> InlineKeyboardMarkup:
    nav_row = []
    if current > 1:
        nav_row.append({"text": "⬅️ Назад", "callback_data": f"prod_page_{current - 1}"})
    if current < total:
        nav_row.append({"text": "➡️ Далее", "callback_data": f"prod_page_{current + 1}"})

    return make_inline_keyboard([
        nav_row,
        [{"text": "➕ Добавить в корзину", "callback_data": f"add_{product_id}"}],
        [{"text": "🔙 Назад", "callback_data": "view_catalog"}]
    ])

def get_paginated_keyboard(items, page: int, callback_prefix: str, item_callback_template: str, items_per_page=4) -> InlineKeyboardMarkup:
    total_pages = ceil(len(items) / items_per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * items_per_page
    end = start + items_per_page
    keyboard_items = items[start:end]

    rows = [[{"text": getattr(item, "name", getattr(item, "question", str(item))), "callback_data": item_callback_template.format(item.id)}] for item in keyboard_items]

    nav_row = []
    if page > 1:
        nav_row.append({"text": "⬅️", "callback_data": f"{callback_prefix}_page_{page - 1}"})
    if page < total_pages:
        nav_row.append({"text": "➡️", "callback_data": f"{callback_prefix}_page_{page + 1}"})
    if nav_row:
        rows.append(nav_row)

    rows.append([{"text": "🔙 Назад", "callback_data": "go_to_start"}])
    return make_inline_keyboard(rows)

def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    return make_reply_keyboard([
        [{"text": "📱 Отправить номер телефона", "request_contact": True}]
    ])

def get_payment_keyboard(order_id: int, pay_url: str = None) -> InlineKeyboardMarkup:
    buttons = []
    if pay_url:
        buttons.append([{"text": "💳 Перейти к оплате", "url": pay_url}])
    else:
        buttons.append([{"text": "💳 Оплатить заказ", "callback_data": f"pay_order_{order_id}"}])
    return make_inline_keyboard(buttons)
