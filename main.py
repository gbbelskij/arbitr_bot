from aiogram import Bot, Dispatcher
import asyncio
import config

# Импорт контроллеров
from bot.handlers import start, project_info, blogger, menu_blogger, seller, menu_seller, offer_seller, offer_blogger, blogger_seller  # Импорт обоих контроллеров

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Регистрация хэндлеров из контроллеров
dp.include_router(start.router)
dp.include_router(project_info.router)  # Регистрация роутера для project_info
dp.include_router(blogger.router)
dp.include_router(menu_blogger.router)
dp.include_router(seller.router)
dp.include_router(menu_seller.router)
dp.include_router(offer_seller.router)
dp.include_router(offer_blogger.router)

async def main():
    # Запуск long-polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
