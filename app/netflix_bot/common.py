import base64
from typing import Tuple


def safe_encode(text: str) -> Tuple[str, str]:
    """Безопасное кодирование до 28 символов."""
    result = base64.b64encode(bytes(text, "utf8"))
    while len(result) > 28:
        text = text[:-1]
        result = base64.b64encode(bytes(text, "utf8"))

    return result.decode(), text


def decodeb64(b64: str) -> str:
    """Декодирование в строку из b64."""
    return base64.b64decode(bytes(b64, "utf8")).decode()
