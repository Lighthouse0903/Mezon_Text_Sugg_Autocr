from pathlib import Path
import csv


def load_vocab(path="data/autocorrect/processed/vocab.csv", min_freq=1):
    vocab = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for word, freq in reader:
            freq = int(freq)
            if freq >= min_freq:
                vocab[word] = freq
    return vocab


def edit_distance(a: str, b: str) -> int:
    la, lb = len(a), len(b)
    dp = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        dp[i][0] = i
    for j in range(lb + 1):
        dp[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
    return dp[la][lb]


def generate_candidates(word: str, vocab: dict, max_distance=2, top_k=5):
    cands = []
    for v, freq in vocab.items():
        if abs(len(v) - len(word)) > max_distance:
            continue
        dist = edit_distance(word, v)
        if dist <= max_distance:
            score = (max_distance - dist) * 1_000_000 + freq
            cands.append((v, score))
    cands.sort(key=lambda x: x[1], reverse=True)
    return [w for w, _ in cands[:top_k]]


if __name__ == "__main__":
    vocab = load_vocab()
    while True:
        w = input("Từ cần sửa: ").strip().lower()
        if not w:
            break
        c = generate_candidates(w, vocab)
        print("→ Gợi ý:", c)
