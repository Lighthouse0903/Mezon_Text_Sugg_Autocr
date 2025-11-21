import os
from tqdm import tqdm
import Levenshtein

input_file = "data/autocorrect/autocorrect_pairs.txt"
output_file = "data/autocorrect/autocorrect_pairs.cleaned.txt"

if not os.path.exists(input_file):
    raise FileNotFoundError(f"Không tìm thấy file: {input_file}")

with open(input_file, "r", encoding="utf-8") as f:
    pairs = [line.strip().split("\t") for line in f if "\t" in line]

print(f"Tổng số cặp ban đầu: {len(pairs):,}")

cleaned = []
for noisy, correct in tqdm(pairs, desc="Đang lọc"):
    dist = Levenshtein.distance(noisy, correct)

    if 0 < dist <= 5:
        cleaned.append((noisy, correct))

print(f"Lọc xong! Giữ lại: {len(cleaned):,} cặp hợp lệ.")

os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    for noisy, correct in cleaned:
        f.write(f"{noisy}\t{correct}\n")

print(f"File kết quả: {output_file}")
