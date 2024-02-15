import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, html, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from aiogram.utils.markdown import hbold

import fileworker
from config_reader import config

# Bot token can be obtained via https://t.me/BotFather
TOKEN = config.bot_token.get_secret_value()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     """
#     This handler receives messages with `/start` command
#     """
#     # Most event objects have aliases for API methods that can be called in events' context
#     # For example if you want to answer to incoming message you can use `message.answer(...)` alias
#     # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
#     # method automatically or call API method directly via
#     # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
#     await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    data = {
        "url": "<N/A>",
    }
    # message.entities
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)  # type: ignore

    url = html.quote(data["url"])
    if fileworker.is_tiktok_url(url):
        # await message.reply("Ok. i'm working, bro.. 5 sec.")
        filename = fileworker.get_mdown(url)
        videofile = FSInputFile(filename)
        await message.delete()
        await bot.send_video(message.chat.id, videofile)
        await fileworker.remove_file(filename)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())