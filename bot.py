# pylint: disable=C0116, C0115, C0114

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

from config_reader import config
from downloader import DownloadService

TOKEN = config.bot_token.get_secret_value()
default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TOKEN, session=AiohttpSession(), default=default_properties)
dp = Dispatcher()


@dp.message()
async def echo_handler(message: types.Message) -> None:
    data = {
        "url": "<N/A>",
    }
    # message.entities
    entities = message.entities or []
    for item in entities:
        if item.type in data:
            data[item.type] = item.extract_from(message.text)  # type: ignore

    url = html.quote(data["url"])
    ds = DownloadService()
    filename = await ds.download(url)

    async def publish_video(filename):
        videofile = FSInputFile(filename)
        await bot.send_video(message.chat.id, videofile)
        await message.delete()
        await ds.remove_file(filename)

    if filename:
        await publish_video(filename)
    else:
        ds.refresh_tiktok_services()
        logging.error("can't download %s", url)
        await publish_video(filename)


async def main() -> None:
    # use pooling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
