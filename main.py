import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from src.config_reader import config
from src.handlers import GroupMessageHandler

BOT_TOKEN = config.bot_token.get_secret_value()


async def main() -> None:
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, session=AiohttpSession(), default=default_properties)
    dp = Dispatcher()

    group_handler = GroupMessageHandler(bot)
    dp.message.register(group_handler.handle_group_message)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
