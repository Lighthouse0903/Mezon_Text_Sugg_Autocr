import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
from tqdm import tqdm
import os


class AutocorrectDataset(Dataset):
    def __init__(self, path, vocab=None):
        self.pairs = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "\t" in line:
                    src, tgt = line.strip().split("\t")
                    self.pairs.append((src.lower(), tgt.lower()))

        if vocab is None:
            chars = sorted({c for s, t in self.pairs for c in (s + t)})
            self.vocab = ["<pad>", "<sos>", "<eos>", "<unk>"] + chars
            self.char2idx = {c: i for i, c in enumerate(self.vocab)}
        else:
            self.vocab = vocab
            self.char2idx = {c: i for i, c in enumerate(vocab)}

    def encode(self, text, max_len=40):
        tokens = [
            self.char2idx.get(c, self.char2idx["<unk>"]) for c in text[: max_len - 2]
        ]
        tokens = [self.char2idx["<sos>"]] + tokens + [self.char2idx["<eos>"]]
        tokens += [self.char2idx["<pad>"]] * (max_len - len(tokens))
        return torch.tensor(tokens)

    def __getitem__(self, idx):
        src, tgt = self.pairs[idx]
        return self.encode(src), self.encode(tgt)

    def __len__(self):
        return len(self.pairs)


class TransformerAutocorrect(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = nn.Parameter(torch.randn(1, 100, d_model))
        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
            batch_first=True,
        )
        self.fc = nn.Linear(d_model, vocab_size)

    def forward(self, src, tgt):
        src_emb = self.embedding(src) + self.pos_encoder[:, : src.size(1), :]
        tgt_emb = self.embedding(tgt) + self.pos_encoder[:, : tgt.size(1), :]
        out = self.transformer(src_emb, tgt_emb)
        return self.fc(out)


def train_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Using device:", device)

    train_data = AutocorrectDataset("data/autocorrect/train.txt")
    val_data = AutocorrectDataset("data/autocorrect/val.txt", vocab=train_data.vocab)

    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=64)

    model = TransformerAutocorrect(vocab_size=len(train_data.vocab)).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss(ignore_index=train_data.char2idx["<pad>"])

    best_loss = float("inf")

    for epoch in range(10):
        model.train()
        total_loss = 0
        for src, tgt in tqdm(train_loader, desc=f"Epoch {epoch+1}/10"):
            src, tgt = src.to(device), tgt.to(device)
            optimizer.zero_grad()
            output = model(src, tgt[:, :-1])
            loss = criterion(
                output.reshape(-1, len(train_data.vocab)), tgt[:, 1:].reshape(-1)
            )
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Train loss: {total_loss / len(train_loader):.4f}")

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for src, tgt in val_loader:
                src, tgt = src.to(device), tgt.to(device)
                out = model(src, tgt[:, :-1])
                loss = criterion(
                    out.reshape(-1, len(train_data.vocab)), tgt[:, 1:].reshape(-1)
                )
                val_loss += loss.item()
        avg_val_loss = val_loss / len(val_loader)
        print(f"Val loss: {avg_val_loss:.4f}")

        # Lưu mô hình tốt nhất
        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            os.makedirs("checkpoints", exist_ok=True)
            torch.save(
                {"model_state": model.state_dict(), "vocab": train_data.vocab},
                "checkpoints/autocorrect_best.pt",
            )
            print("Saved best model!")


if __name__ == "__main__":
    train_model()
