# импорты 
import asyncio
import logging
import time

from aiogram import Bot, Dispatcher, F, exceptions, filters, html, types
from aiogram.types import ContentType, FSInputFile

import fileworker
from config_reader import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Для записей с типом Secret* необходимо
# вызывать метод get_secret_value(),
# чтобы получить настоящее содержимое вместо '*******'
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
Command = filters.command.Command


@dp.message(F.)
async def exctact_url(message: types.Message):
    data = {
        "url": "<N/A>",
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract(message.text)  # type: ignore
    url = html.quote(data["url"])
    if fileworker.is_tiktok_url(url):
        # await message.reply("Ok. i'm working, bro.. 5 sec.")
        filename = fileworker.get_mdown(url)
        videofile = FSInputFile(filename)
        await message.delete()
        await bot.send_video(message.chat.id, videofile)
        await fileworker.remove_file(filename)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except exceptions.TelegramRetryAfter:
            time.sleep(10)
