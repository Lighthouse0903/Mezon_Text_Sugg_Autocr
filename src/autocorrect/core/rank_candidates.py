import math
from pathlib import Path
import csv
from src.autocorrect.core.generate_candidate import edit_distance


def load_vocab(path="data/autocorrect/processed/vocab.csv", min_freq=1):
    vocab = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for w, c in reader:
            c = int(c)
            if c >= min_freq:
                vocab[w] = c
    return vocab


def rank_candidates(word, vocab, max_distance=2, top_k=5):
    candidates = []
    for v, freq in vocab.items():
        if abs(len(v) - len(word)) > max_distance:
            continue
        dist = edit_distance(word, v)
        if dist <= max_distance:
            score = (max_distance - dist + 1) * math.log(freq + 1)
            candidates.append((v, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [w for w, _ in candidates[:top_k]]


if __name__ == "__main__":
    vocab = load_vocab()
    while True:
        w = input("Từ cần sửa: ").strip().lower()
        if not w:
            break
        c = rank_candidates(w, vocab)
        print("→ Gợi ý:", c)
