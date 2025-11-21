from src.autosuggest.lm.ngram import NGramLM
import pathlib

pathlib.Path("models").mkdir(exist_ok=True)
lm = NGramLM(n=3, discount=0.75, extra_pool=200)
lm.fit_file("data/split/train.txt")
lm.save("models/ngram.pkl")
print("saved -> models/ngram.pkl")
