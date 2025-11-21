from pathlib import Path, re

SRC = Path("data/autocorrect/processed/data200k.vi.txt")
OUT = Path("data/autocorrect/processed/corpus_vi_clean.txt")

def clean_line(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

lines = SRC.read_text(encoding="utf-8").splitlines()
cleaned = [clean_line(l) for l in lines if len(l.strip()) > 0]
OUT.write_text("\n".join(cleaned), encoding="utf-8")
print(f"Clean done: {len(cleaned):,} lines → {OUT}")
