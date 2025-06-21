# bot/texts.py

TEXTS = {
    "start": "Привет, {first_name}! 👋\nДобро пожаловать в наш магазин.\nДля просмотра каталога нажмите кнопку ниже.",

    "choose_category": "Выберите категорию:",
    "choose_subcategory": "Выберите подкатегорию:",
    "products_empty": "Товары пока не добавлены.",

    "cart_empty": "Ваша корзина пуста.",
    "cart_all_deleted": "Все товары удалены из корзины.",
    "cart_item_deleted": "🗑️ Товар удален из корзины.",

    "quantity_prompt": "Укажите количество:",
    "invalid_quantity": "Введите корректное количество.",
    "confirm_quantity": "<b>{product_name}</b>\nКоличество: {quantity}\nОбщая стоимость: {total}₽",
    "add_success": "🛒 Товар добавлен в корзину!",
    "add_cancelled": "❌ Добавление отменено.",

    "enter_name": "Введите ваше имя для оформления заказа:",
    "enter_address": "Введите адрес доставки:",
    "share_phone": "📞 Нажмите кнопку ниже, чтобы поделиться номером телефона:",
    "phone_received": "Спасибо, номер получен.",

    "order_success": "✅ Ваш заказ успешно оформлен!\n💵 Сумма к оплате: {total}₽\n\n🔗 Нажмите кнопку ниже для имитации оплаты:",
    "order_paid": "✅ Оплата успешно имитирована. Спасибо за заказ!",

    "page_not_found": "Нет такой страницы",
    "delete_error": "Ошибка удаления.",
    "cart_load_failed": "Не удалось получить корзину пользователя.",
    "faq_title": "❓ Часто задаваемые вопросы:",
}


def get_text(key: str, **kwargs) -> str:
    """Возвращает форматированный текст по ключу."""
    text = TEXTS.get(key, "")
    return text.format(**kwargs) if kwargs else text
