import argparse, random, pathlib, re
from typing import List, Tuple


def tokenize(s: str) -> List[str]:
    return re.findall(r"\w+|[^\w\s]", s, flags=re.UNICODE)


def stratified_split(lines: List[str], ratios: Tuple[float, float, float], seed: int):
    bins = {0: [], 1: [], 2: [], 3: [], 4: []}
    for s in lines:
        n = len(tokenize(s))
        b = 0 if n <= 5 else 1 if n <= 10 else 2 if n <= 20 else 3 if n <= 40 else 4
        bins[b].append(s)

    tr, va, te = [], [], []
    random.seed(seed)
    for arr in bins.values():
        random.shuffle(arr)
        n = len(arr)
        n_tr = int(ratios[0] * n)
        n_va = int(ratios[1] * n)
        tr += arr[:n_tr]
        va += arr[n_tr : n_tr + n_va]
        te += arr[n_tr + n_va :]
    return tr, va, te


def simple_split(lines: List[str], ratios: Tuple[float, float, float], seed: int):
    random.seed(seed)
    random.shuffle(lines)
    n = len(lines)
    n_tr = int(ratios[0] * n)
    n_va = int(ratios[1] * n)
    return lines[:n_tr], lines[n_tr : n_tr + n_va], lines[n_tr + n_va :]


def main():
    ap = argparse.ArgumentParser(description="Split corpus into train/valid/test")
    ap.add_argument(
        "--input",
        default="data/processed/corpus.cleaned.txt",
        help="Đường dẫn file đầu vào (mỗi câu một dòng)",
    )
    ap.add_argument("--outdir", default="data/split", help="Thư mục xuất kết quả")
    ap.add_argument("--train", type=float, default=0.90, help="Tỷ lệ train")
    ap.add_argument("--valid", type=float, default=0.05, help="Tỷ lệ valid")
    ap.add_argument("--test", type=float, default=0.05, help="Tỷ lệ test")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    ap.add_argument(
        "--stratify-by-length",
        action="store_true",
        help="Bật chia theo độ dài câu để giữ phân phối",
    )
    args = ap.parse_args()

    assert (
        abs((args.train + args.valid + args.test) - 1.0) < 1e-6
    ), "Tổng tỷ lệ phải = 1.0"

    inp = pathlib.Path(args.input)
    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    lines = inp.read_text("utf-8").splitlines()
    lines = [s.strip() for s in lines if s.strip()]

    ratios = (args.train, args.valid, args.test)
    if args.stratify_by_length:
        train, valid, test = stratified_split(lines, ratios, args.seed)
    else:
        train, valid, test = simple_split(lines, ratios, args.seed)

    (outdir / "train.txt").write_text("\n".join(train), "utf-8")
    (outdir / "valid.txt").write_text("\n".join(valid), "utf-8")
    (outdir / "test.txt").write_text("\n".join(test), "utf-8")

    print(f"Done. Train/Valid/Test = {len(train)}/{len(valid)}/{len(test)} → {outdir}")


if __name__ == "__main__":
    main()
