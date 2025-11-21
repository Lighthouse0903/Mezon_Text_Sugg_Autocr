import re
from collections import Counter
from pathlib import Path

CORPUS_PATH = Path("data/autocorrect/processed/autocorrect_pairs.cleaned.txt")

VOCAB_PATH = Path("data/autocorrect/processed/vocab.csv")


def build_vocab(corpus_path=CORPUS_PATH, output_path=VOCAB_PATH):
    print(f"Đang đọc corpus từ: {corpus_path}")
    text = corpus_path.read_text(encoding="utf-8").lower()

    words = re.findall(
        r"[a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọ"
        r"ôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+",
        text,
    )

    print(f"Tổng số từ thu được: {len(words):,}")

    word_freq = Counter(words)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for w, c in word_freq.most_common():
            f.write(f"{w},{c}\n")

    print(f"Đã tạo xong: {output_path}")
    print(f"Tổng số từ duy nhất: {len(word_freq):,}")


if __name__ == "__main__":
    build_vocab()
