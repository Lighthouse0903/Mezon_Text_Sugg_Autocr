import regex as re, unicodedata, pathlib

inp = "data/processed/corpus.txt"
outp = "data/processed/corpus.cleaned.txt"
out = []
seen = set()
with open(inp, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        s = unicodedata.normalize("NFC", line).strip().lower()
        if not s:
            continue
        s = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL]", s)
        s = re.sub(r"\b(?:\+?\d[\d\s\-\.\(\)]{7,})\b", "[PHONE]", s)
        s = re.sub(r"\b\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?\b", "[NUM]", s)
        s = re.sub(r"\b(?=\d)\d{4,}\b", "[NUM]", s)
        toks = re.findall(r"\w+|[^\w\s]", s)
        if 3 <= len(toks) <= 60 and s not in seen:
            seen.add(s)
            out.append(s)
pathlib.Path(outp).write_text("\n".join(out), "utf-8")
print("kept:", len(out))
