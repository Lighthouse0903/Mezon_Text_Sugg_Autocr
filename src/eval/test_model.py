import argparse, random, time, statistics, re
from typing import Optional, List, Dict
from src.lm.ngram import NGramLM, tok

WORD_RE = re.compile(r"^\w+$", flags=re.UNICODE)


def is_word(t: str) -> bool:
    return WORD_RE.match(t) is not None


def reciprocal_rank(rank: int) -> float:
    return 1.0 / rank if rank < 10**9 else 0.0


def eval_file(
    model: NGramLM,
    path: str,
    k: int = 5,
    prefix_chars: int = 0,
    max_samples: Optional[int] = 2000,
    skip_punct: bool = True,
    seed: int = 0,
) -> Dict:
    lines = open(path, "r", encoding="utf-8").read().splitlines()
    if max_samples is not None and max_samples < len(lines):
        random.seed(seed)
        random.shuffle(lines)
        lines = lines[:max_samples]

    ranks: List[int] = []
    lat_ms: List[float] = []
    kept = 0

    for s in lines:
        t = tok(s)
        if len(t) < 2:
            continue
        target = t[-1]
        if skip_punct and not is_word(target):  # bỏ dấu câu khi chấm
            continue
        prefix = target[:prefix_chars] if prefix_chars > 0 else None
        ctx = " ".join(t[:-1])

        t0 = time.perf_counter()
        cands = model.suggest(ctx, prefix=prefix, k=k)
        lat_ms.append((time.perf_counter() - t0) * 1000.0)

        rank = cands.index(target) + 1 if target in cands else 10**9
        ranks.append(rank)
        kept += 1

    if not ranks:
        return {
            "n": 0,
            "hit@k": 0.0,
            "mrr": 0.0,
            "p50_ms": 0.0,
            "p95_ms": 0.0,
        }

    hitk = sum(1 for r in ranks if r <= k) / len(ranks)
    mrr = sum(reciprocal_rank(r) for r in ranks) / len(ranks)
    p50 = statistics.median(lat_ms)
    p95 = sorted(lat_ms)[int(0.95 * len(lat_ms)) - 1]
    return {
        "n": kept,
        "hit@k": hitk,
        "mrr": mrr,
        "p50_ms": p50,
        "p95_ms": p95,
    }


def interactive(model: NGramLM, k: int = 5):
    print("Interactive mode. Enter context; prefix optional. Blank line to exit.")
    while True:
        try:
            ctx = input("\ncontext> ").strip()
            if not ctx:
                break
            pre = input("prefix (optional)> ").strip()
            pre = pre if pre else None
            cands = model.suggest(ctx, prefix=pre, k=k)
            print("top-{}: {}".format(k, ", ".join(cands)))
        except (EOFError, KeyboardInterrupt):
            break


def main():
    ap = argparse.ArgumentParser(
        description="Test NGram model (interactive or file eval)."
    )
    ap.add_argument("--model", default="models/ngram.pkl")
    ap.add_argument("--k", type=int, default=5)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("interactive", help="Run interactive tester")
    s1.add_argument("--k", type=int, default=5)

    s2 = sub.add_parser("file", help="Evaluate on a text file (one sentence per line)")
    s2.add_argument("--data", default="data/split/valid.txt")
    s2.add_argument(
        "--prefix-chars",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="0=no prefix; 1/2=prefix length",
    )
    s2.add_argument(
        "--samples", type=int, default=2000, help="max samples to eval (None = all)"
    )
    s2.add_argument(
        "--keep-punct", action="store_true", help="include punctuation targets in eval"
    )
    s2.add_argument("--seed", type=int, default=0)

    args = ap.parse_args()
    lm = NGramLM.load(args.model)

    if args.cmd == "interactive":
        interactive(lm, k=args.k)
    else:
        res = eval_file(
            lm,
            path=args.data,
            k=args.k,
            prefix_chars=args.prefix_chars,
            max_samples=(args.samples if args.samples > 0 else None),
            skip_punct=(not args.keep_punct),
            seed=args.seed,
        )
        print(
            f"[file={args.data}] n={res['n']} | Hit@{args.k}={res['hit@k']:.3f} "
            f"| MRR={res['mrr']:.3f} | p50={res['p50_ms']:.1f}ms | p95={res['p95_ms']:.1f}ms"
        )


if __name__ == "__main__":
    main()
