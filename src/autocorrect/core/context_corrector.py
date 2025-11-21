import re
import csv
from collections import Counter
from math import log
from pathlib import Path
from rank_candidates import rank_candidates, load_vocab, edit_distance
from normalize_vi import normalize_vi
from keyboard_fix import fix_common_keyboard
from hard_rules import apply_hard_rules
import math


def build_bigram_model(
    corpus_path="data/autocorrect/processed/corpus_vi_clean.txt",
    output_path="data/autocorrect/processed/bigram.csv",
):

    print("Đang đọc corpus...")
    text = Path(corpus_path).read_text(encoding="utf-8").lower()
    words = re.findall(
        r"[a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọ"
        r"ôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+",
        text,
    )
    bigrams = Counter(zip(words[:-1], words[1:]))
    with open(output_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        for (w1, w2), c in bigrams.most_common():
            writer.writerow([w1, w2, c])
    print(f"Đã lưu bigram model: {output_path} ({len(bigrams):,} cặp từ)")


def load_bigram(path="data/autocorrect/processed/bigram.csv", min_freq=2):
    bigram = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                continue
            w1, w2, c = row
            c = int(c)
            if c >= min_freq:
                bigram.setdefault(w1, {})[w2] = c
    return bigram


def correct_sentence(sentence, vocab, bigram, max_distance=2, top_k=3):
    words = sentence.lower().split()
    corrected = [words[0]]

    for i in range(1, len(words)):
        w = words[i]

        ruled = apply_hard_rules(w)
        if ruled != w:
            corrected.append(ruled)
            continue

        if w in vocab:
            corrected.append(w)
            continue

        cands = rank_candidates(w, vocab, max_distance=max_distance, top_k=top_k)
        prev = corrected[-1]
        best_cand, best_score = cands[0], -1e9

        for cand in cands:
            bigram_freq = bigram.get(prev, {}).get(cand, 1)
            unigram_freq = vocab.get(cand, 1)
            dist = edit_distance(w, cand)

            score = (
                0.6 * math.log(bigram_freq + 1)
                + 1.2 * math.log(unigram_freq + 1)
                - 2.0 * dist
            )

            if score > best_score:
                best_cand, best_score = cand, score

        corrected.append(best_cand)

    return " ".join(corrected)


if not Path("data/autocorrect/processed/bigram.csv").exists():
    build_bigram_model()

if __name__ == "__main__":
    vocab = load_vocab()
    bigram = load_bigram()
    while True:
        s = input("Nhập câu: ").strip()
        if not s:
            break
        s = normalize_vi(s)

        tokens = s.split()
        tokens = [apply_hard_rules(t) for t in tokens]

        tokens = [fix_common_keyboard(t) for t in tokens]

        s = " ".join(tokens)

        print("→", correct_sentence(s, vocab, bigram))
