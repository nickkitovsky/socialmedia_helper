import logging
from time import time

import tiktok_downloader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TikTokDownloader:
    MIN_FILE_SIZE_BYTES = 99999

    def __init__(self) -> None:
        self.services = list(tiktok_downloader.services)

    async def download(self, url: str) -> str | None:
        filename = f"tmp_files/tt_{int(time())}.mp4"
        for service_name in self.services:
            available_videos = tiktok_downloader.services[service_name](url)
            filtered_video = [
                v for v in available_videos if v.type == "video" and not v.watermark
            ]
            if filtered_video:
                for video in filtered_video:
                    try:
                        if video.get_size() < self.MIN_FILE_SIZE_BYTES:
                            continue
                    except KeyError:
                        continue
                    else:
                        video.download(filename)
                        self._service_to_top(service_name)
                        logger.info("%s downloaded from %s", url, service_name)
                        return filename
        return None

    def _service_to_top(self, service_name: str) -> None:
        if service_index := self.services.index(service_name) != 0:
            self.services.pop(service_index)
            self.services.insert(0, service_name)
