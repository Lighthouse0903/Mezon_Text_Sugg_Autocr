import argparse
import regex as re
import unicodedata
import pathlib

VIETNAMESE_CHARS = "ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệóòỏõọốồổỗộớờởỡợúùủũụứừửữựíìỉĩịýỳỷỹỵ"


def is_vietnamese_word(word: str) -> bool:
    return any(ch in VIETNAMESE_CHARS for ch in word.lower())


def clean_corpus(input_path, output_path, min_len=3, max_len=60, only_vi=False):
    out = []
    seen = set()

    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = unicodedata.normalize("NFC", line).strip().lower()
            if not s:
                continue

            toks = re.findall(r"\w+|[^\w\s]", s)

            # lọc độ dài
            if not (min_len <= len(toks) <= max_len):
                continue

            if only_vi:
                vi_count = sum(is_vietnamese_word(t) for t in toks)
                if vi_count / len(toks) < 0.5:
                    continue

            if s not in seen:
                seen.add(s)
                out.append(s)

    pathlib.Path(output_path).write_text("\n".join(out), "utf-8")
    print(f"Done. Kept {len(out)} sentences. Saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean text corpus")
    parser.add_argument("--input", type=str, required=True, help="Input corpus file")
    parser.add_argument("--output", type=str, required=True, help="Output cleaned file")
    parser.add_argument(
        "--min-len", type=int, default=3, help="Minimum tokens per sentence"
    )
    parser.add_argument(
        "--max-len", type=int, default=60, help="Maximum tokens per sentence"
    )
    parser.add_argument(
        "--only-vi", action="store_true", help="Keep only Vietnamese sentences"
    )

    args = parser.parse_args()

    clean_corpus(
        args.input,
        args.output,
        min_len=args.min_len,
        max_len=args.max_len,
        only_vi=args.only_vi,
    )
