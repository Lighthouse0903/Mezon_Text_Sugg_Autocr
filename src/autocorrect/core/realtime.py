from src.autocorrect.core.normalize_vi import normalize_vi
from src.autocorrect.core.hard_rules import apply_hard_rules
from src.autocorrect.core.keyboard_fix import fix_common_keyboard


KEEP_IF_USER_TYPED = {
    "trời",
    "trời",
    "mây",
    "máy",
    "may",
    "mà",
    "mã",
    "thật",
    "thiệt",
    "nay",
    "hôm",
    "này",
}


def autocorrect_token_live(token: str) -> str:
    if not token:
        return token

    w = normalize_vi(token).strip()

    if w in KEEP_IF_USER_TYPED:
        return w

    fixed = apply_hard_rules(w)
    if fixed != w:
        return fixed

    kb = fix_common_keyboard(w)
    if kb != w:
        return kb

    return token


def autocorrect_line_live(text: str) -> str:
    return " ".join(autocorrect_token_live(t) for t in text.split())
