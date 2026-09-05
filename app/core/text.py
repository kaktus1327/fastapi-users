import unicodedata

_SPECIAL = str.maketrans({"ł": "l", "Ł": "L", "ø": "o", "Ø": "O", "đ": "d", "Đ": "D"})


def fold(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.translate(_SPECIAL))
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return stripped.casefold().strip()
