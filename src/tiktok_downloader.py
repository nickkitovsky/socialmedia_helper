import contextlib
import logging
from asyncio import sleep as asleep
from pathlib import Path
from time import time
from typing import Callable

import tiktok_downloader

SERVICES_FILE = ".tiktok_services"
MINIMUM_FILE_SIZE_BYTES = 99999
# mdown very slow service, but it works sometimes
# therefore self.services = [working, MDOWN, not_working]
MDOWN = "mdown"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TikTokDownloader:
    def __init__(self) -> None:
        self.services = self._load_services()
        # Delete mdown and add it after working services
        # FIX: fix it later $)
        with contextlib.suppress(KeyError):
            tiktok_downloader.services.pop(MDOWN)
        self._all_services: dict[str, Callable] = tiktok_downloader.services.items()  # type: ignore

    async def download(self, url: str) -> str | None:
        if not self.services:
            self._refresh_services(url)
            self._dump_services()
            logger.debug("Wait 1sec. for some API limit.")
            await asleep(1)
        filename = f"tmp_files/tt_{int(time())}.mp4"
        for service_name in self.services:
            available_videos = tiktok_downloader.services[service_name](url)
            filtered_video = [
                v for v in available_videos if v.type == "video" and not v.watermark
            ]
            if filtered_video:
                for video in filtered_video:
                    try:
                        if video.get_size() < MINIMUM_FILE_SIZE_BYTES:
                            continue
                    except KeyError:
                        continue
                    else:
                        video.download(filename)
                        self._service_to_top(service_name)
                        logger.info("%s downloaded from %s", url, service_name)
                        return filename
        return None

    def _dump_services(self) -> None:
        Path(SERVICES_FILE).write_text("\n".join(self.services), encoding="utf-8")

    @staticmethod
    def _load_services() -> list[str | None]:
        try:
            return Path(SERVICES_FILE).read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []

    def _service_to_top(self, service_name: str) -> None:
        if service_index := self.services.index(service_name) != 0:
            self.services.pop(service_index)
            self.services.insert(0, service_name)

    def _refresh_services(self, url: str) -> None:
        working_service_names = []
        not_working_service_names = []
        for service_name, download_func in tiktok_downloader.services.items():
            try:
                download_func(url)
            # FIX: add concrete exceptions
            except Exception:  # noqa: PERF203
                not_working_service_names.append(service_name)
                logger.exception("%s is not working", service_name)
            else:
                working_service_names.append(service_name)
                logger.info("%s is working", service_name)

        if not working_service_names:
            logger.critical("all tiktok services not working for %s", url)
        self.services = [*working_service_names, MDOWN, *not_working_service_names]
