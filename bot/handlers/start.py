from aiogram import types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from store.models import TelegramUser, Cart
from keyboards.inline import get_start_keyboard
from loader import dp
from texts.texts import get_text
from asgiref.sync import sync_to_async
import os

LINK = os.environ.get("LINK")

# Универсальный метод
async def cmd_start_base(message_or_callback: Message | CallbackQuery, state: FSMContext):
    user = message_or_callback.from_user

    tg_user, created = await TelegramUser.objects.aget_or_create(
        id=user.id,
        defaults={
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
        }
    )

    if created:
        await Cart.objects.acreate(user=tg_user)
    else:
        try:
            _ = await sync_to_async(lambda: tg_user.cart)()
        except Cart.DoesNotExist:
            await Cart.objects.acreate(user=tg_user)

    text = get_text("start", first_name=user.first_name)
    reply_markup = get_start_keyboard()

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=reply_markup)
    else:
        await message_or_callback.answer(text, reply_markup=reply_markup)


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await cmd_start_base(message, state)


@dp.callback_query(F.data == "go_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        get_text("start", first_name=callback.from_user.first_name),
        reply_markup=get_start_keyboard()
    )
