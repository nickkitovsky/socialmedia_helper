import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from src.config_reader import config
from src.handlers import GroupMessageHandler
from src.logger_config import setup_logging

BOT_TOKEN = config.bot_token.get_secret_value()

setup_logging(debug=False)
logger = logging.getLogger(__name__)


async def main() -> None:
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, session=AiohttpSession(), default=default_properties)
    dp = Dispatcher()

    group_handler = GroupMessageHandler(bot)
    dp.message.register(group_handler.handle_group_message)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.debug("Bot is starting.")
    asyncio.run(main())
