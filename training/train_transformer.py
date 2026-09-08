from __future__ import annotations
import argparse, json, random
from pathlib import Path
import numpy as np, pandas as pd, torch
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer
from clinroute.transformer_model import MultiTaskTransformer


class ReferralDataset(Dataset):
    def __init__(self, frame, tokenizer, route_map, urgency_map, max_length=256):
        self.frame = frame.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.route_map = route_map
        self.urgency_map = urgency_map
        self.max_length = max_length

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, idx):
        row = self.frame.iloc[idx]
        enc = self.tokenizer(
            str(row["text"]),
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"][0],
            "attention_mask": enc["attention_mask"][0],
            "route": torch.tensor(self.route_map[row["route"]]),
            "urgency": torch.tensor(self.urgency_map[row["urgency"]]),
        }


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def evaluate(model, loader, device):
    model.eval()
    rt = []
    rp = []
    ut = []
    up = []
    with torch.inference_mode():
        for b in loader:
            r, u = model(b["input_ids"].to(device), b["attention_mask"].to(device))
            rt.extend(b["route"].tolist())
            ut.extend(b["urgency"].tolist())
            rp.extend(r.argmax(1).cpu().tolist())
            up.extend(u.argmax(1).cpu().tolist())
    return {
        "route_macro_f1": float(f1_score(rt, rp, average="macro")),
        "urgency_macro_f1": float(f1_score(ut, up, average="macro")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic_referrals.csv")
    ap.add_argument("--encoder", default="distilroberta-base")
    ap.add_argument("--output", default="models/transformer")
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--max-length", type=int, default=256)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    seed_all(a.seed)
    frame = pd.read_csv(a.data)
    train, val = train_test_split(
        frame,
        test_size=0.2,
        random_state=a.seed,
        stratify=frame["route"].astype(str) + "::" + frame["urgency"].astype(str),
    )
    routes = sorted(frame.route.unique())
    urgencies = sorted(frame.urgency.unique())
    rm = {x: i for i, x in enumerate(routes)}
    um = {x: i for i, x in enumerate(urgencies)}
    tok = AutoTokenizer.from_pretrained(a.encoder)
    tr = ReferralDataset(train, tok, rm, um, a.max_length)
    va = ReferralDataset(val, tok, rm, um, a.max_length)
    tl = DataLoader(tr, batch_size=a.batch_size, shuffle=True)
    vl = DataLoader(va, batch_size=a.batch_size)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MultiTaskTransformer(a.encoder, len(routes), len(urgencies)).to(device)
    opt = AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    loss_fn = nn.CrossEntropyLoss()
    best = -1
    best_state = None
    hist = []
    for epoch in range(1, a.epochs + 1):
        model.train()
        losses = []
        for b in tl:
            opt.zero_grad(set_to_none=True)
            r, u = model(b["input_ids"].to(device), b["attention_mask"].to(device))
            loss = loss_fn(r, b["route"].to(device)) + loss_fn(u, b["urgency"].to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            losses.append(float(loss.detach().cpu()))
        result = evaluate(model, vl, device)
        result.update(epoch=epoch, train_loss=float(np.mean(losses)))
        hist.append(result)
        score = (result["route_macro_f1"] + result["urgency_macro_f1"]) / 2
        if score > best:
            best = score
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    model.load_state_dict(best_state)
    tok.save_pretrained(out / "tokenizer")
    model.encoder.save_pretrained(out / "encoder")
    torch.save(model.state_dict(), out / "multitask_state.pt")
    (out / "metadata.json").write_text(
        json.dumps(
            {
                "encoder": a.encoder,
                "route_labels": routes,
                "urgency_labels": urgencies,
                "max_length": a.max_length,
                "validation_history": hist,
                "benchmark_scope": "synthetic_data_only",
            },
            indent=2,
        )
    )
    (out / "VERSION").write_text("dual-head-transformer-synthetic-v1\n")


if __name__ == "__main__":
    main()
