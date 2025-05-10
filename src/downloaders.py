import logging
import pathlib
from time import time

import tiktok_downloader

logger = logging.getLogger(__name__)


class TikTokDownloader:
    MIN_FILE_SIZE_BYTES = 99999

    def __init__(self) -> None:
        # delete mdown
        services_without_mdown = tiktok_downloader.services
        services_without_mdown.pop("mdown")
        self.services = list(services_without_mdown)
        self.tmp_dir = pathlib.Path("tmp_files")
        self._ensure_tmp_dir_exists()

    def _ensure_tmp_dir_exists(self) -> None:
        if not self.tmp_dir.exists():
            pathlib.Path.mkdir(self.tmp_dir)
            logger.info("Created temporary directory: %s", self.tmp_dir)

    async def download(self, url: str) -> str | None:
        filename = f"tmp_files/tt_{int(time())}.mp4"
        for service_name in self.services:
            logger.debug(
                "Attempting download from service: %s for URL: %s",
                service_name,
                url,
            )
            try:
                available_videos = tiktok_downloader.services[service_name](url)
                filtered_video = [
                    v for v in available_videos if v.type == "video" and not v.watermark
                ]
                if filtered_video:
                    for video in filtered_video:
                        try:
                            file_size = video.get_size()
                            if file_size < self.MIN_FILE_SIZE_BYTES:
                                logger.debug(
                                    "Skipping video from %s, size %s bytes.",
                                    service_name,
                                    file_size,
                                )
                                continue
                        except KeyError:
                            continue
                        else:
                            video.download(filename)
                            self._service_to_top(service_name)
                            logger.info(
                                "Successfully downloaded %s from %s to %s",
                                url,
                                service_name,
                                filename,
                            )
                            return filename

            except Exception as e:  # noqa: BLE001
                logger.info("Error, %s is unavailable, %s", service_name, e)
        return None

    def _service_to_top(self, service_name: str) -> None:
        if service_index := self.services.index(service_name) != 0:
            self.services.pop(service_index)
            self.services.insert(0, service_name)
