import re
from src.autocorrect.core.rank_candidates import load_vocab, rank_candidates

VOCAB = load_vocab()
TELEX_MAP = {
    "aw": "ă",
    "aa": "â",
    "dd": "đ",
    "ee": "ê",
    "oo": "ô",
    "ow": "ơ",
    "uw": "ư",
}

TONE_MAP = {
    "s": 1,  # sắc
    "f": 2,  # huyền
    "r": 3,  # hỏi
    "x": 4,  # ngã
    "j": 5,  # nặng
}


def telex_to_vietnamese(word: str) -> str:
    tone = None
    tones = [ch for ch in word if ch in TONE_MAP]

    if tones:
        tone = TONE_MAP[tones[-1]]
        for t in tones:
            word = word.replace(t, "")

    for k, v in TELEX_MAP.items():
        word = word.replace(k, v)

    if tone:
        word = add_vietnamese_tone(word, tone)

    return word


def is_valid_vi_word(word: str, vocab: dict) -> bool:
    if word in vocab:
        return True
    return bool(re.search(r"[aeiouyăâêôơưáàảãạéèẻẽẹóòỏõọúùủũụíìỉĩịýỳỷỹỵ]", word))


def add_vietnamese_tone(word, tone):
    vowels = {
        "a": ["á", "à", "ả", "ã", "ạ"],
        "ă": ["ắ", "ằ", "ẳ", "ẵ", "ặ"],
        "â": ["ấ", "ầ", "ẩ", "ẫ", "ậ"],
        "e": ["é", "è", "ẻ", "ẽ", "ẹ"],
        "ê": ["ế", "ề", "ể", "ễ", "ệ"],
        "i": ["í", "ì", "ỉ", "ĩ", "ị"],
        "o": ["ó", "ò", "ỏ", "õ", "ọ"],
        "ô": ["ố", "ồ", "ổ", "ỗ", "ộ"],
        "ơ": ["ớ", "ờ", "ở", "ỡ", "ợ"],
        "u": ["ú", "ù", "ủ", "ũ", "ụ"],
        "ư": ["ứ", "ừ", "ử", "ữ", "ự"],
        "y": ["ý", "ỳ", "ỷ", "ỹ", "ỵ"],
    }

    for v in reversed(range(len(word))):
        ch = word[v]
        if ch in vowels:
            word = word[:v] + vowels[ch][tone - 1] + word[v + 1 :]
            break
    return word


VOWELS = "aeiouyăâêôơưáàảãạéèẻẽẹóòỏõọúùủũụíìỉĩịýỳỷỹỵ"


def share_vowel(a, b):
    return any(v in a and v in b for v in VOWELS)


def fix_common_keyboard(word: str) -> str:
    w_fixed = telex_to_vietnamese(word)
    if w_fixed in VOCAB:
        return w_fixed

    filtered_vocab = {w: f for w, f in VOCAB.items() if share_vowel(w_fixed, w)}

    if not filtered_vocab:
        filtered_vocab = VOCAB

    candidates = rank_candidates(w_fixed, filtered_vocab, max_distance=2, top_k=1)
    if candidates:
        return candidates[0]
    return word
