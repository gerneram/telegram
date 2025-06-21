import re
from aiogram import F, Router
from aiogram.types import CallbackQuery
from store.models import FAQ
from keyboards.inline import make_inline_keyboard, get_list_keyboard
from texts.texts import get_text
from loader import dp


@dp.callback_query(F.data == "view_faq")
async def view_faq(callback: CallbackQuery):
    faqs = [faq async for faq in FAQ.objects.all()]
    keyboard = get_list_keyboard(faqs, prefix="faq")

    # Добавим кнопку «Назад» вручную
    keyboard.inline_keyboard.append([
        {"text": "🔙 Назад", "callback_data": "go_to_start"}
    ])
    if callback.message.text != get_text("faq_title"):
        await callback.message.edit_text(get_text("faq_title"), reply_markup=keyboard)
    else:
        await callback.message.edit_reply_markup(reply_markup=keyboard)


def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

@dp.callback_query(F.data.startswith("faq_"))
async def show_faq_answer(callback: CallbackQuery):
    if callback.data == "faq_back":
        return await view_faq(callback)

    faq_id = int(callback.data.split("_")[1])
    faq = await FAQ.objects.aget(pk=faq_id)

    keyboard = make_inline_keyboard([
        [{"text": "🔙 Назад", "callback_data": "faq_back"}]
    ])

    await callback.message.edit_text(
    f"*{escape_markdown(faq.question)}*\n\n{escape_markdown(faq.answer)}",
    parse_mode="MarkdownV2",
    reply_markup=keyboard
    )
