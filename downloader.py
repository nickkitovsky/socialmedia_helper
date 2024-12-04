# pylint: disable=C0116, C0115, C0114
import logging
import pathlib
from asyncio import sleep as asleep
from time import time
from urllib.parse import urlparse

import tiktok_downloader

ANY_TIKTOK_URL = "https://vt.tiktok.com/ZSjCtNtdu/"
TIKTOK_SERVICES_FILE = ".tiktok_services"


class DownloadService:
    def __init__(self) -> None:
        self.tiktok_services = self.load_tiktok_services()

    async def remove_file(
        self, filename: pathlib.Path | str, sleeptime: int = 5 * 60
    ):
        await asleep(sleeptime)
        pathlib.Path(filename).unlink()

    async def download(self, url: str):
        if "tiktok" in urlparse(url).netloc:
            downloader = TikTokDownloader(url, self.tiktok_services)
        try:
            downloaded_filename = downloader.download()  # pylint:disable=E0606
            return downloaded_filename
        except UnboundLocalError:
            logging.error("%s not downloaded")

    def _scan_tiktok_working_services(self) -> list[str]:
        working_services = []
        for service, download in tiktok_downloader.services.items():
            try:
                download(ANY_TIKTOK_URL)
            except Exception:  # pylint: disable=W0718
                logging.error("%s is not working", service)
            else:
                logging.info("%s is working", service)
                working_services.append(service)
        if not working_services:
            logging.critical("all tiktok services not working")
        return working_services

    def load_tiktok_services(self):
        try:
            with open(TIKTOK_SERVICES_FILE, mode="r", encoding="utf-8") as fo:
                return fo.readlines()
        except FileNotFoundError:
            working_services = self._scan_tiktok_working_services()
            with open(TIKTOK_SERVICES_FILE, mode="w", encoding="utf-8") as fo:
                fo.writelines(working_services)
            return working_services

    def refresh_tiktok_services(self):
        pathlib.Path(TIKTOK_SERVICES_FILE).unlink()
        self.load_tiktok_services()


class TikTokDownloader:
    def __init__(self, url: str, download_services: list[str]) -> None:
        self.url = url
        self.download_services = download_services
        self.filename = f"tmp_files/tt_{int(time())}.mp4"

    def download(self) -> str | None:
        for service in self.download_services:
            available_videos = tiktok_downloader.services[service](self.url)
            try:
                video = self._select_video(available_videos)
            except IndexError:
                logging.error(
                    "%s can't download video (%s)",
                    service,
                    self.url,
                )
                continue
            else:
                video.download(self.filename)
                logging.info("%s downloaded from %s", self.url, service)
                return self.filename
        return None

    def _select_video(
        self,
        available_videos: list[tiktok_downloader.utils.Download],
    ) -> tiktok_downloader.utils.Download:
        def is_conditions(v: tiktok_downloader.utils.Download) -> bool:
            if v.type == "video" and not v.watermark and v.render:
                return True
            return False

        return [v for v in available_videos if is_conditions(v)][0]
