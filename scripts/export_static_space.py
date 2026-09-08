"""Export the validated scikit-learn baseline into a portable Static Space bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess  # nosec B404 - fixed git read-only command

import joblib

from clinroute.redaction import redact_obvious_identifiers


EXAMPLES = [
    "ENT referral for ear pain for 1 week. Finding: inflamed tympanic membrane. urgent assessment is requested.",
    "ENT referral for gradual hearing loss for 3 months. Finding: failed hearing screen. routine specialist review is requested.",
    "ENT referral for nasal obstruction for 2 weeks. Finding: nasal polyp. earlier specialist review is requested.",
    "ENT referral for hoarseness for 4 weeks. Finding: persistent dysphonia. urgent assessment is requested.",
]


def serialize_pipeline(path: Path) -> dict:
    pipeline = joblib.load(path)
    tfidf = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]
    if tuple(tfidf.ngram_range) != (1, 2) or not tfidf.sublinear_tf or tfidf.norm != "l2":
        raise ValueError("Static runtime currently supports the versioned (1,2) sublinear L2 TF-IDF contract")
    return {
        "classes": [str(x) for x in clf.classes_],
        "vocabulary": {str(k): int(v) for k, v in tfidf.vocabulary_.items()},
        "idf": [float(x) for x in tfidf.idf_],
        "coef": [[float(x) for x in row] for row in clf.coef_],
        "intercept": [float(x) for x in clf.intercept_],
        "sublinear_tf": True,
        "ngram_range": [1, 2],
        "norm": "l2",
        "token_pattern": tfidf.token_pattern,
        "lowercase": bool(tfidf.lowercase),
    }


def expected(pipeline, text: str) -> dict:
    cleaned = redact_obvious_identifiers(text)
    probabilities = pipeline.predict_proba([cleaned])[0]
    classes = [str(x) for x in pipeline.classes_]
    idx = int(probabilities.argmax())
    return {
        "label": classes[idx],
        "confidence": float(probabilities[idx]),
        "probabilities": {label: float(probabilities[i]) for i, label in enumerate(classes)},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models", type=Path, default=Path("models/baseline"))
    parser.add_argument("--evaluation", type=Path, default=Path("evaluation/candidate_metrics.json"))
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    for name in ("README.md", "index.html", "styles.css", "runtime.js", "app.js"):
        shutil.copyfile(root / "hf_static" / name, out / name)

    revision = subprocess.check_output(  # nosec B603 - fixed read-only git command
        [shutil.which("git") or "/usr/bin/git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    route_pipeline = joblib.load(root / args.models / "route.joblib")
    urgency_pipeline = joblib.load(root / args.models / "urgency.joblib")
    version = (root / args.models / "VERSION").read_text().strip()

    model = {
        "model_version": version,
        "source_revision": revision,
        "runtime_contract": "sklearn-tfidf-logreg-browser-v1",
        "route": serialize_pipeline(root / args.models / "route.joblib"),
        "urgency": serialize_pipeline(root / args.models / "urgency.joblib"),
    }
    (out / "model.json").write_text(json.dumps(model, separators=(",", ":"), sort_keys=True))

    report = json.loads((root / args.evaluation).read_text())
    report["static_space_source_revision"] = revision
    report["portable_runtime_contract"] = model["runtime_contract"]
    (out / "evaluation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    fixtures = []
    for text in EXAMPLES:
        fixtures.append(
            {
                "text": text,
                "route": expected(route_pipeline, text),
                "urgency": expected(urgency_pipeline, text),
            }
        )
    (out / "validation.json").write_text(json.dumps(fixtures, indent=2, sort_keys=True) + "\n")
    print(f"Exported validated static bundle to {out}")


if __name__ == "__main__":
    main()
