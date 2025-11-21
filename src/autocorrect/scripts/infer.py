import torch
import torch.nn as nn
from autocorrect.scripts.autocorrect_model import TransformerAutocorrect


device = "cuda" if torch.cuda.is_available() else "cpu"

# === Load checkpoint ===
checkpoint_path = "checkpoints/autocorrect_best.pt"
checkpoint = torch.load(checkpoint_path, map_location=device)

vocab = checkpoint["vocab"]
char2idx = {c: i for i, c in enumerate(vocab)}
idx2char = {i: c for i, c in enumerate(vocab)}

model = TransformerAutocorrect(vocab_size=len(vocab)).to(device)
model.load_state_dict(checkpoint["model_state"])
model.eval()

print(f"Loaded model from {checkpoint_path} (vocab: {len(vocab)} chars)")


def encode(text, max_len=40):
    tokens = [char2idx.get(c, char2idx["<unk>"]) for c in text[: max_len - 2]]
    tokens = [char2idx["<sos>"]] + tokens + [char2idx["<eos>"]]
    tokens += [char2idx["<pad>"]] * (max_len - len(tokens))
    return torch.tensor(tokens).unsqueeze(0).to(device)


def decode(token_ids):
    chars = []
    for i in token_ids:
        ch = idx2char.get(i, "")
        if ch in ["<sos>", "<pad>", "<eos>"]:
            continue
        chars.append(ch)
    return "".join(chars)


def autocorrect(input_text, max_len=40):
    src = encode(input_text)
    tgt = torch.tensor([[char2idx["<sos>"]]], device=device)

    for _ in range(max_len):
        with torch.no_grad():
            out = model(src, tgt)
        next_token = out[:, -1, :].argmax(-1)
        tgt = torch.cat([tgt, next_token.unsqueeze(0)], dim=1)

        # Debug xem model sinh ra gì
        print("Raw tokens:", [idx2char.get(i.item(), "?") for i in next_token])

        if next_token.item() == char2idx["<eos>"]:
            break

    decoded = decode(tgt[0].tolist())
    print("Decoded sequence:", decoded)
    return decoded if decoded else "(không thể sửa được)"


if __name__ == "__main__":
    print("Autocorrect Inference Ready!")
    while True:
        text = input("Nhập từ sai: ").strip().lower()
        if text == "":
            break
        print("➡", autocorrect(text))
