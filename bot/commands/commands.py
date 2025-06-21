from aiogram.types import BotCommand

async def set_bot_commands(bot):
    commands = [
        BotCommand(command="start", description="🔹 Начать"),
        BotCommand(command="help", description="📘 Помощь"),
        BotCommand(command="cart", description="🛒 Корзина"),
        BotCommand(command="faq", description="❓ Частые вопросы")
    ]
    await bot.set_my_commands(commands)
