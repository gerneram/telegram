import os
import django
import asyncio
from commands.commands import set_bot_commands
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
django.setup()

from loader import bot, dp
from handlers import cart,catalog,order,start,faq_handlers

async def main():
    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
