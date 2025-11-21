import os
import torch
import torch.nn as nn


pairs = []
with open("data/autocorrect/autocorrect_pairs.cleaned.txt", "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            noisy, correct = parts
            pairs.append((noisy, correct))

chars = set()
for noisy, correct in pairs:
    chars.update(list(noisy))
    chars.update(list(correct))

PAD = "<pad>"
SOS = "<sos>"
EOS = "<eos>"

itos = [PAD, SOS, EOS] + sorted(chars)
stoi = {ch: i for i, ch in enumerate(itos)}

vocab_size = len(itos)
print("Total pairs:", len(pairs))
print("Vocab size:", vocab_size)


def encode(text):
    return [stoi[SOS]] + [stoi.get(c, stoi[PAD]) for c in text] + [stoi[EOS]]


def decode(seq):
    return "".join([itos[i] for i in seq if i not in (stoi[PAD], stoi[SOS], stoi[EOS])])


class Seq2Seq(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=stoi[PAD])
        self.encoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, src, tgt):
        emb_src = self.embedding(src)
        _, (h, c) = self.encoder(emb_src)
        emb_tgt = self.embedding(tgt[:, :-1])
        out, _ = self.decoder(emb_tgt, (h, c))
        logits = self.fc(out)
        return logits

    def predict(self, src, max_len=50):
        """Greedy decoding"""
        self.eval()
        with torch.no_grad():
            emb_src = self.embedding(src)
            _, (h, c) = self.encoder(emb_src)

            inp = torch.tensor([[stoi[SOS]]], device=src.device)
            output_seq = []

            for _ in range(max_len):
                emb = self.embedding(inp)
                out, (h, c) = self.decoder(emb, (h, c))
                logits = self.fc(out[:, -1, :])
                pred_id = torch.argmax(logits, dim=-1).item()
                if pred_id == stoi[EOS]:
                    break
                output_seq.append(pred_id)
                inp = torch.tensor([[pred_id]], device=src.device)

            return output_seq


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Seq2Seq(vocab_size).to(device)

model_path = "models/autocorrect_lstm.pt"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model not found at {model_path}, hãy train trước!")

model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()
print(f"Loaded model from {model_path}")


while True:
    noisy = input("Nhập từ sai: ").strip()
    if not noisy:
        break

    src_tensor = torch.tensor([encode(noisy)], dtype=torch.long, device=device)
    pred_ids = model.predict(src_tensor, max_len=50)
    corrected = decode(pred_ids)

    print(f"➡ {noisy}  →  {corrected}")
