#!/usr/bin/env python3
"""
Generate noisy <tab> correct pairs from a Vietnamese wordlist.

Usage:
  python src/data/generate_noisy_pairs.py \
    --wordlist data/Viet74K.txt \
    --out data/autocorrect_pairs.txt \
    --variants 3 \
    --seed 42
"""

import argparse
import random
from pathlib import Path
from typing import List, Tuple


def delete_char(word: str) -> str:
    if len(word) <= 1:
        return word
    i = random.randrange(len(word))
    return word[:i] + word[i + 1 :]


def insert_char(word: str, charset: List[str]) -> str:
    i = random.randrange(len(word) + 1)
    c = random.choice(charset)
    return word[:i] + c + word[i:]


def substitute_char(word: str, charset: List[str]) -> str:
    if not word:
        return word
    i = random.randrange(len(word))
    c = random.choice(charset)
    return word[:i] + c + word[i + 1 :]


def transpose_char(word: str) -> str:
    if len(word) < 2:
        return word
    i = random.randrange(len(word) - 1)
    return word[:i] + word[i + 1] + word[i] + word[i + 2 :]


def generate_noisy_variant(word: str, charset: List[str]) -> str:
    ops = [delete_char, insert_char, substitute_char, transpose_char]
    op = random.choice(ops)
    return op(word) if op not in (insert_char, substitute_char) else op(word, charset)


def build_charset(words: List[str]) -> List[str]:
    charset = sorted({ch for w in words for ch in w})
    return charset


def generate_pairs(
    words: List[str], variants_per_word: int = 2, seed: int = 42
) -> List[Tuple[str, str]]:
    random.seed(seed)
    charset = build_charset(words)
    pairs = []
    for w in words:
        w = w.strip().lower()
        if len(w) < 2:
            continue
        for _ in range(variants_per_word):
            noisy = generate_noisy_variant(w, charset)
            if noisy != w:
                pairs.append((noisy, w))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--wordlist", required=True, help="Vietnamese wordlist (one word per line)"
    )
    ap.add_argument("--out", default="data/autocorrect_pairs.txt", help="Output file")
    ap.add_argument(
        "--variants", type=int, default=2, help="Number of noisy variants per word"
    )
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    args = ap.parse_args()

    words = Path(args.wordlist).read_text(encoding="utf-8").splitlines()
    pairs = generate_pairs(words, args.variants, args.seed)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for noisy, correct in pairs:
            f.write(f"{noisy}\t{correct}\n")

    print(f"Saved {len(pairs)} pairs to {out_path}")
    print("Example:")
    for noisy, correct in pairs[:20]:
        print(f"{noisy} -> {correct}")


if __name__ == "__main__":
    main()
