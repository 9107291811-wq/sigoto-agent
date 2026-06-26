import json
from typing import Any


def as_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False).lower()
    except TypeError:
        return str(value).lower()
