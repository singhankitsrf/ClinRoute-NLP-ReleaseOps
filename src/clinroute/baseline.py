from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib


@dataclass
class BaselineBundle:
    route_model: Any
    urgency_model: Any
    version: str = "tfidf-logreg"

    @classmethod
    def load(cls, model_dir: str | Path) -> "BaselineBundle":
        model_dir = Path(model_dir)
        version_file = model_dir / "VERSION"
        version = version_file.read_text().strip() if version_file.exists() else "tfidf-logreg"
        return cls(
            route_model=joblib.load(model_dir / "route.joblib"),
            urgency_model=joblib.load(model_dir / "urgency.joblib"),
            version=version,
        )

    def predict(self, text: str) -> dict[str, Any]:
        route_p = self.route_model.predict_proba([text])[0]
        route_classes = self.route_model.classes_
        route_idx = int(route_p.argmax())

        urgency_p = self.urgency_model.predict_proba([text])[0]
        urgency_classes = self.urgency_model.classes_
        urgency_idx = int(urgency_p.argmax())

        return {
            "route": str(route_classes[route_idx]),
            "route_confidence": float(route_p[route_idx]),
            "urgency": str(urgency_classes[urgency_idx]),
            "urgency_confidence": float(urgency_p[urgency_idx]),
        }
