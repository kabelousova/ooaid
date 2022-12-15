import asyncio

from async_bot.telegram_bot import AsyncBot
from database.models import get_sessionmaker
from news_notification import news_notification


async def main():
    sessionmaker = get_sessionmaker()
    bot = AsyncBot(sessionmaker)

    asyncio.create_task(news_notification(bot.bot, sessionmaker))

    await bot.start()


if __name__ == '__main__':
    asyncio.run(main())