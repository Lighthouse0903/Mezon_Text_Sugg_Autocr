from src.lm.ngram import NGramLM, tok
import random

lm = NGramLM.load("models/ngram.pkl")
lines = open("data/split/valid.txt", "r", encoding="utf-8").read().splitlines()
random.seed(0)
lines = lines[:2000]

ranks = []
for s in lines:
    t = tok(s)
    if len(t) < 2:
        continue
    ctx, target = " ".join(t[:-1]), t[-1]
    cands = lm.suggest(ctx, prefix=None, k=5)
    ranks.append(cands.index(target) + 1 if target in cands else 10**9)

hit5 = sum(1 for r in ranks if r <= 5) / len(ranks)
mrr = sum(1 / (r if r < 10**9 else 10**9) for r in ranks) / len(ranks)
print(f"Hit@5={hit5:.3f} | MRR={mrr:.3f} | Samples={len(ranks)}")
