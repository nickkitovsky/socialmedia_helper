from time import time
from urllib.parse import urlparse
from tiktok_downloader import snaptik
from tiktok_downloader import mdown
from asyncio import sleep as asleep
import pathlib


# cloudfare problem
def get_snaptik(url: str) -> str:
    data = snaptik(url)
    filename = f"snaptik_{int(time())}.mp4"
    data[0].download(filename)
    return filename


def get_mdown(url: str) -> str:
    data = mdown(url)
    filename = f"tmp_files/mdown_{int(time())}.mp4"
    data[0].download(filename)
    return filename


def download(url: str) -> str:
    filename = get_mdown(url)
    return filename


async def remove_file(filename: str, sleeptime: int = 5 * 60):
    await asleep(sleeptime)
    pathlib.Path(filename).unlink()


def is_tiktok_url(url: str) -> bool:
    parsed_url = urlparse(url)
    if parsed_url.hostname == "vt.tiktok.com" or parsed_url.hostname == "www.tiktok.com":
        return True
    else:
        return False
