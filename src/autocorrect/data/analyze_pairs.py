import collections

pairs_file = "data/autocorrect/autocorrect_pairs.txt"

pairs = []
with open(pairs_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            noisy, correct = parts
            pairs.append((noisy, correct))

print(f"Tổng số cặp: {len(pairs):,}")

counter = collections.Counter([noisy for noisy, _ in pairs])

print("\nTop 50 lỗi sai phổ biến nhất:\n")
for noisy, freq in counter.most_common(50):
    corrections = {correct for n, correct in pairs if n == noisy}
    print(f"{noisy:20s}  →  {', '.join(corrections)}   ({freq} lần)")
