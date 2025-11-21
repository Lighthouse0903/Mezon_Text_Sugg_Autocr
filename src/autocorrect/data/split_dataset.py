import random
from sklearn.model_selection import train_test_split

INPUT_FILE = "data/autocorrect/autocorrect_pairs.cleaned.txt"
TRAIN_FILE = "data/autocorrect/train.txt"
VAL_FILE = "data/autocorrect/val.txt"

TRAIN_RATIO = 0.9

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    pairs = [line.strip() for line in f if "\t" in line]

random.shuffle(pairs)

train_pairs, val_pairs = train_test_split(
    pairs, test_size=1 - TRAIN_RATIO, random_state=42
)

with open(TRAIN_FILE, "w", encoding="utf-8") as f:
    for p in train_pairs:
        f.write(p + "\n")

with open(VAL_FILE, "w", encoding="utf-8") as f:
    for p in val_pairs:
        f.write(p + "\n")

print(f"Tổng số cặp: {len(pairs)}")
print(f"Train: {len(train_pairs)}")
print(f"Val: {len(val_pairs)}")
print("Đã tạo xong train.txt và val.txt!")
