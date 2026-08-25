from __future__ import annotations

import torch
from torch import nn


class MultiTaskTransformer(nn.Module):
    def __init__(
        self,
        encoder_name: str,
        n_routes: int,
        n_urgencies: int,
        dropout: float = 0.20,
        encoder_revision: str | None = None,
        local_files_only: bool = False,
    ) -> None:
        super().__init__()
        from transformers import AutoModel

        # Remote models should be called with an immutable revision supplied by
        # the training workflow. Inference from exported local artifacts sets
        # local_files_only=True and does not contact the Hub.
        self.encoder = AutoModel.from_pretrained(
            encoder_name,
            revision=encoder_revision,
            local_files_only=local_files_only,
        )
        hidden = int(self.encoder.config.hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.route_head = nn.Linear(hidden, n_routes)
        self.urgency_head = nn.Linear(hidden, n_urgencies)

    def forward(self, input_ids, attention_mask):
        output = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.dropout(output.last_hidden_state[:, 0])
        return self.route_head(pooled), self.urgency_head(pooled)
