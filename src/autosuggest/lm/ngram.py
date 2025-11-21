from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import pickle, re, collections
import unicodedata


def tok(s: str) -> List[str]:
    return re.findall(r"\w+|[^\w\s]", s, flags=re.UNICODE)


def strip_diacritics(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn"
    )


class NGramLM:
    def __init__(self, n: int = 3, discount: float = 0.75, extra_pool: int = 200):
        assert n >= 2, "n must be >= 2"
        self.n = n
        self.D = float(discount)
        self.extra_pool = int(extra_pool)

        self.ng: List[collections.Counter] = [collections.Counter() for _ in range(n)]
        self.next_map: Dict[Tuple[str, ...], Dict[str, int]] = {}
        self.vocab: set[str] = set()

        self.cont_count: Dict[str, int] = collections.Counter()
        self.total_unique_bigrams: int = 0

        self.prefix2: Dict[str, List[str]] = {}
        self.prefix3: Dict[str, List[str]] = {}

    def fit_file(self, path: str) -> None:
        pad = ["<s>"] * (self.n - 1)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                t = pad + tok(line) + ["</s>"]

                for w in t:
                    self.vocab.add(w)

                L = len(t)
                for k in range(1, self.n + 1):
                    cnt = self.ng[k - 1]
                    for i in range(L - k + 1):
                        cnt[tuple(t[i : i + k])] += 1

                for i in range(L - self.n + 1):
                    ngram = tuple(t[i : i + self.n])
                    hist, w = ngram[:-1], ngram[-1]
                    m = self.next_map.get(hist)
                    if m is None:
                        m = {}
                        self.next_map[hist] = m
                    m[w] = m.get(w, 0) + 1

        self._build_continuation_counts()
        self._build_prefix_index()

    def _build_continuation_counts(self) -> None:
        bigram_keys = self.ng[1].keys()
        cc = collections.Counter()
        for u_w in bigram_keys:
            w = u_w[-1]
            cc[w] += 1
        self.cont_count = cc
        self.total_unique_bigrams = len(self.ng[1]) if self.ng[1] else 1

    @staticmethod
    def _pkey2(w: str) -> str:
        w = w.lower()
        return w[:2] if len(w) >= 2 else (w + "_" * (2 - len(w)))

    @staticmethod
    def _pkey3(w: str) -> str:
        w = w.lower()
        return w[:3] if len(w) >= 3 else (w + "_" * (3 - len(w)))

    def _build_prefix_index(self) -> None:
        """Build prefix indices for 2 & 3 chars, sorted by continuation popularity."""
        p2: Dict[str, List[str]] = collections.defaultdict(list)
        p3: Dict[str, List[str]] = collections.defaultdict(list)
        for w in self.vocab:
            if w in {"<s>", "</s>"}:
                continue
            p2[self._pkey2(w)].append(w)
            p3[self._pkey3(w)].append(w)
        keyf = lambda w: self.cont_count.get(w, 0)
        for d in (p2, p3):
            for k, arr in d.items():
                arr.sort(key=keyf, reverse=True)
        self.prefix2 = dict(p2)
        self.prefix3 = dict(p3)

    def _cont_prob(self, w: str) -> float:
        return self.cont_count.get(w, 0) / self.total_unique_bigrams

    def _hist_stats(self, hist: Tuple[str, ...]) -> Tuple[int, int, Dict[str, int]]:
        cdict = self.next_map.get(hist)
        if not cdict:
            return 0, 0, {}
        denom = sum(cdict.values())
        return denom, len(cdict), cdict

    def suggest(
        self, context: str, prefix: Optional[str] = None, k: int = 5
    ) -> List[str]:
        prefix = (prefix or "").strip()
        ctx_tokens = tok(context)
        ctx = tuple(
            ["<s>"] * max(0, self.n - 1 - len(ctx_tokens)) + ctx_tokens[-(self.n - 1) :]
        )

        denom, uniq_next, cdict = self._hist_stats(ctx)
        D = self.D

        pre_l = prefix.lower()
        pre_f = strip_diacritics(pre_l) if prefix else ""

        def _starts(w: str) -> bool:
            if not prefix:
                return True
            wl = w.lower()
            return wl.startswith(pre_l) or strip_diacritics(wl).startswith(pre_f)

        def _keep(w: str) -> bool:
            if w in {"<s>", "</s>"}:
                return False
            if prefix and len(w) < 2:
                return False
            if not any(ch.isalnum() for ch in w):
                return False
            return True

        def _weight(w: str) -> float:
            """Ưu tiên từ có dấu khi bạn gõ không dấu; hạ điểm ascii-only."""
            if not prefix:
                return 1.0
            wl = w.lower()
            exact = wl.startswith(pre_l)
            folded = strip_diacritics(wl).startswith(pre_f)
            wgt = 1.0
            if folded and not exact:
                wgt *= 1.12
            if all(ord(c) < 128 for c in wl) and any(ch.isalpha() for ch in wl):
                wgt *= 0.90
            return wgt

        observed = list(cdict.keys())
        cand_set = {w for w in observed if _starts(w) and _keep(w)}

        if prefix:
            extras: List[str] = []
            if len(prefix) >= 3 and hasattr(self, "prefix3") and self.prefix3:
                e3 = self.prefix3.get(self._pkey3(prefix), [])
                extras.extend(e3)
                if len(extras) < self.extra_pool:
                    seen = set(extras)
                    e2 = self.prefix2.get(self._pkey2(prefix), [])
                    extras.extend([w for w in e2 if w not in seen])
            else:
                key2 = (
                    self._pkey2(prefix)
                    if hasattr(self, "_pkey2")
                    else self._pkey(prefix)
                )
                extras = self.prefix2.get(key2, [])

            for w in extras[: self.extra_pool]:
                if _starts(w) and _keep(w):
                    cand_set.add(w)

        if denom == 0:
            scored = [(w, self._cont_prob(w) * _weight(w)) for w in cand_set]
            scored.sort(key=lambda x: x[1], reverse=True)
            return [w for w, _ in scored[:k]]

        lambda_w = (D * uniq_next) / denom
        scored: List[Tuple[str, float]] = []
        for w in cand_set:
            num = cdict.get(w, 0)
            p_ml = max(num - D, 0.0) / denom
            p = (p_ml + lambda_w * self._cont_prob(w)) * _weight(w)
            scored.append((w, p))

        if not scored and not prefix:
            extras = sorted(
                (w for w in self.vocab if _keep(w)),
                key=lambda w: self._cont_prob(w),
                reverse=True,
            )[: self.extra_pool]
            scored = [(w, lambda_w * self._cont_prob(w) * _weight(w)) for w in extras]

        scored.sort(key=lambda x: x[1], reverse=True)
        return [w for w, _ in scored if _keep(w)][:k]

    def save(self, path: str) -> None:
        if not self.prefix2 or not self.prefix3:
            self._build_prefix_index()
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "n": self.n,
                    "D": self.D,
                    "extra_pool": self.extra_pool,
                    "ng": self.ng,
                    "next_map": self.next_map,
                    "vocab": self.vocab,
                    "cont_count": self.cont_count,
                    "total_unique_bigrams": self.total_unique_bigrams,
                    "prefix2": self.prefix2,
                    "prefix3": self.prefix3,
                },
                f,
                protocol=pickle.HIGHEST_PROTOCOL,
            )

    @staticmethod
    def load(path: str) -> "NGramLM":
        with open(path, "rb") as f:
            state = pickle.load(f)
        obj = NGramLM(
            n=state["n"], discount=state["D"], extra_pool=state.get("extra_pool", 200)
        )
        obj.ng = state["ng"]
        obj.next_map = state["next_map"]
        obj.vocab = state["vocab"]
        obj.cont_count = state["cont_count"]
        obj.total_unique_bigrams = state["total_unique_bigrams"]
        obj.prefix2 = state.get("prefix2", {})
        obj.prefix3 = state.get("prefix3", {})
        if not obj.prefix2 or not obj.prefix3:
            obj._build_prefix_index()
        return obj
