# handlers.py
import pathlib
from asyncio import sleep as asleep

from aiogram import Bot
from aiogram.types import FSInputFile, Message

from src.link_detector import is_tiktok_url
from src.tiktok_downloader import TikTokDownloader

WAIT_FOR_DELETE_FILE_SEC = 5 * 60


class GroupMessageHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.tiktok_downloader = TikTokDownloader()

    async def handle_group_message(self, message: Message) -> None:
        if not message.text:
            return

        if not is_tiktok_url(message.text):
            return

        file_path = await self.tiktok_downloader.download(message.text)
        if file_path:
            await self.bot.send_video(
                chat_id=message.chat.id,
                video=FSInputFile(file_path),
            )
            await message.delete()
            await asleep(WAIT_FOR_DELETE_FILE_SEC)
            pathlib.Path(file_path).unlink()

    @staticmethod
    async def remove_file(
        filename: pathlib.Path | str,
        sleeptime: int = 5 * 60,
    ) -> None:
        await asleep(sleeptime)
        pathlib.Path(filename).unlink()
