import re
import unicodedata


def normalize_vi(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFC", text)
    text = re.sub(
        r"[^a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệ"
        r"ìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữự"
        r"ỳýỷỹỵđ\s]",
        "",
        text,
    )
    return text.strip()
