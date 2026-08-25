from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from transformers import AutoTokenizer

from .transformer_model import MultiTaskTransformer


class TransformerBundle:
    def __init__(
        self,
        model: MultiTaskTransformer,
        tokenizer: Any,
        route_labels: list[str],
        urgency_labels: list[str],
        max_length: int,
        version: str,
    ) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.route_labels = route_labels
        self.urgency_labels = urgency_labels
        self.max_length = max_length
        self.version = version

    @classmethod
    def load(cls, model_dir: str | Path) -> "TransformerBundle":
        model_dir = Path(model_dir)
        metadata = json.loads((model_dir / "metadata.json").read_text())

        tokenizer = AutoTokenizer.from_pretrained(
            model_dir / "tokenizer",
            revision=None,
            local_files_only=True,
        )
        model = MultiTaskTransformer(
            str(model_dir / "encoder"),
            len(metadata["route_labels"]),
            len(metadata["urgency_labels"]),
            encoder_revision=None,
            local_files_only=True,
        )
        state = torch.load(
            model_dir / "multitask_state.pt",
            map_location="cpu",
            weights_only=True,
        )
        model.load_state_dict(state)
        model.eval()

        version_file = model_dir / "VERSION"
        version = version_file.read_text().strip() if version_file.exists() else "dual-head-transformer"
        return cls(
            model,
            tokenizer,
            list(metadata["route_labels"]),
            list(metadata["urgency_labels"]),
            int(metadata["max_length"]),
            version,
        )

    def predict(self, text: str) -> dict[str, Any]:
        encoded = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        with torch.inference_mode():
            route_logits, urgency_logits = self.model(
                encoded["input_ids"],
                encoded["attention_mask"],
            )
            route_probs = torch.softmax(route_logits, dim=1)[0]
            urgency_probs = torch.softmax(urgency_logits, dim=1)[0]

        route_idx = int(route_probs.argmax())
        urgency_idx = int(urgency_probs.argmax())
        return {
            "route": self.route_labels[route_idx],
            "route_confidence": float(route_probs[route_idx]),
            "urgency": self.urgency_labels[urgency_idx],
            "urgency_confidence": float(urgency_probs[urgency_idx]),
        }
