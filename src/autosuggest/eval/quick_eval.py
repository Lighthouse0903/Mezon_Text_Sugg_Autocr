from __future__ import annotations
import time, math, random, statistics
from typing import List, Tuple, Optional
from src.autosuggest.lm.ngram import NGramLM, tok


MODEL_PATH = "models/ngram.pkl"
VALID_PATH = "data/split/valid.txt"
MAX_SAMPLES = 2000
TOPK = 5
SEED = 0

BIG = 10**9


def load_valid(path: str, limit: Optional[int]) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if limit:
        random.seed(SEED)
        lines = lines[:limit]
    return lines


def rank_of(target: str, cands: List[str]) -> int:
    try:
        return cands.index(target) + 1
    except ValueError:
        return BIG


def hit_at(ranks: List[int], k: int) -> float:
    if not ranks:
        return 0.0
    return sum(1 for r in ranks if r <= k) / len(ranks)


def mrr_at(ranks: List[int], k: int) -> float:
    if not ranks:
        return 0.0
    s = 0.0
    for r in ranks:
        if r <= k:
            s += 1.0 / r
    return s / len(ranks)


def safe_mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def approx_perplexity(
    lm: NGramLM, sentences: List[str], max_tokens: int = 10000
) -> float:

    n = 0
    log2_sum = 0.0
    for s in sentences:
        t = tok(s)
        if len(t) < 2:
            continue
        for i in range(1, len(t)):
            ctx = " ".join(t[:i])
            w = t[i]

            cands = lm.suggest(ctx, prefix=None, k=100)
            if w in cands:
                r = cands.index(w) + 1
                p = 1.0 / (r + 5.0)
            else:
                p = 1e-9
            log2_sum += math.log2(p)
            n += 1
            if n >= max_tokens:
                break
        if n >= max_tokens:
            break
    if n == 0:
        return float("inf")
    return 2 ** (-log2_sum / n)


def eval_mode(lm: NGramLM, sentences: List[str], mode: str) -> Tuple[dict, dict]:
    """
    mode:
      - "none": không prefix
      - "pre1": prefix 1 ký tự
      - "pre2": prefix 2 ký tự
    Return: (metrics, latency_stats)
    """
    ranks: List[int] = []
    latencies: List[float] = []

    for s in sentences:
        t = tok(s)
        if len(t) < 2:
            continue
        ctx_tokens, target = t[:-1], t[-1]
        if target in {"</s>", "<s>"}:
            continue
        ctx = " ".join(ctx_tokens)

        if mode == "none":
            prefix = None
        elif mode == "pre1":
            prefix = target[:1]
            if not prefix:
                prefix = None
        elif mode == "pre2":
            prefix = target[:2]
            if not prefix:
                prefix = None
        else:
            raise ValueError("unknown mode")

        t0 = time.perf_counter()
        cands = lm.suggest(ctx, prefix=prefix, k=TOPK)
        dt = (time.perf_counter() - t0) * 1000.0  # ms
        latencies.append(dt)

        ranks.append(rank_of(target, cands))

    metrics = {
        "samples": len(ranks),
        "hit@1": hit_at(ranks, 1),
        "hit@3": hit_at(ranks, 3),
        "hit@5": hit_at(ranks, 5),
        "mrr@5": mrr_at(ranks, 5),
    }
    latency_stats = {
        "avg_ms": safe_mean(latencies),
        "p95_ms": (
            statistics.quantiles(latencies, n=100)[94]
            if len(latencies) >= 100
            else max(latencies) if latencies else 0.0
        ),
    }
    return metrics, latency_stats


if __name__ == "__main__":
    lm = NGramLM.load(MODEL_PATH)
    lines = load_valid(VALID_PATH, MAX_SAMPLES)

    pp = approx_perplexity(lm, lines, max_tokens=8000)
    print(f"Perplexity≈ {pp:.2f}")

    for mode in ["none", "pre1", "pre2"]:
        metrics, latency = eval_mode(lm, lines, mode)
        print(
            f"[{mode}] "
            f"samples={metrics['samples']} | "
            f"Hit@1={metrics['hit@1']:.3f} | "
            f"Hit@3={metrics['hit@3']:.3f} | "
            f"Hit@5={metrics['hit@5']:.3f} | "
            f"MRR@5={metrics['mrr@5']:.3f} | "
            f"avg={latency['avg_ms']:.1f}ms | p95={latency['p95_ms']:.1f}ms"
        )
