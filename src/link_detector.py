import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def is_tiktok_url(text: str) -> bool:
    try:
        for word in text.split():
            parsed = urlparse(word)
            if parsed.scheme in {"http", "https"} and "tiktok.com" in parsed.netloc:
                logger.debug("Recieved tiktok url: %s", text)
                return True
    except Exception as e:  # noqa: BLE001
        logger.warning("Failure parse message: %s, cause: %s", text, e)
        return False
    else:
        return False
