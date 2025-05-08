from urllib.parse import urlparse


def is_tiktok_url(text: str) -> bool:
    try:
        for word in text.split():
            parsed = urlparse(word)
            if parsed.scheme in {"http", "https"} and "tiktok.com" in parsed.netloc:
                return True
    except Exception:  # noqa: BLE001
        return False
    else:
        return False
