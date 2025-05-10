import asyncio
import logging
import pathlib
from asyncio import sleep as asleep

from aiogram import Bot
from aiogram.types import FSInputFile, Message
from src.downloaders import TikTokDownloader
from src.link_detector import is_tiktok_url

WAIT_FOR_DELETE_FILE_SEC = 5 * 60

logger = logging.getLogger(__name__)


class GroupMessageHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.tiktok = TikTokDownloader()

    async def handle_group_message(self, message: Message) -> None:
        if isinstance(message.text, str) and is_tiktok_url(message.text):
            logger.debug("Handle tiktok url: %s", message.text)
            file_path = await self.tiktok.download(message.text)
            if file_path:
                await self.bot.send_video(
                    chat_id=message.chat.id,
                    video=FSInputFile(file_path),
                )
                await message.delete()

                asyncio.create_task(self._delete_file_later(file_path))  # noqa: RUF006

    async def _delete_file_later(self, file_path: str) -> None:
        await asleep(WAIT_FOR_DELETE_FILE_SEC)
        try:
            pathlib.Path(file_path).unlink()
            logger.debug("Delete %s with delay.", file_path)

        except Exception as e:  # noqa: BLE001
            logger.warning("File is not delete, cause %s", e)
