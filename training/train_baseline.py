"""Reproducible synthetic benchmark; never a clinical-performance estimate."""

from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from clinroute.calibration import expected_calibration_error
from clinroute.redaction import redact_obvious_identifiers


def make_model():
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2), min_df=2, max_features=30000, sublinear_tf=True
                ),
            ),
            ("clf", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42)),
        ]
    )


def metrics(y_true, probs, classes):
    pred = np.asarray(classes)[probs.argmax(axis=1)]
    encoded = np.asarray([classes.index(x) for x in y_true])
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, labels=classes, average="macro", zero_division=0)),
        "ece": expected_calibration_error(encoded, probs),
        "brier_score": float(np.mean(np.sum((probs - np.eye(len(classes))[encoded]) ** 2, axis=1))),
        "labels": classes,
        "confusion_matrix": confusion_matrix(y_true, pred, labels=classes).tolist(),
    }


def benchmark(data, output, metrics_path):
    frame = pd.read_csv(data)
    # Remove identifier tokens BEFORE splitting or fitting. Identical redacted
    # notes cannot appear in both partitions.
    frame["text"] = frame["text"].map(redact_obvious_identifiers)
    frame["text"] = frame["text"].str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    conflicts = frame.groupby("text")[["route", "urgency"]].nunique().max(axis=1)
    if (conflicts > 1).any():
        raise ValueError("Identical normalized notes have conflicting labels")
    input_rows = len(frame)
    frame = frame.drop_duplicates("text").sort_values("text").reset_index(drop=True)
    train, test = train_test_split(
        frame,
        test_size=0.20,
        random_state=42,
        stratify=frame["route"].astype(str) + "::" + frame["urgency"].astype(str),
    )
    report = {
        "benchmark_scope": "synthetic_data_only",
        "protocol": "redacted-deduplicated-v2",
        "seed": 42,
        "input_rows": input_rows,
        "unique_notes": len(frame),
        "train_samples": len(train),
        "test_samples": len(test),
        "train_test_text_overlap": len(set(train.text) & set(test.text)),
        "dataset_sha256": hashlib.sha256(Path(data).read_bytes()).hexdigest(),
        "normalized_corpus_sha256": hashlib.sha256(
            frame[["text", "route", "urgency"]].to_csv(index=False).encode()
        ).hexdigest(),
        "limitations": [
            "Templated synthetic referrals; urgency is explicitly stated in input.",
            "Shared vocabulary across splits; does not establish real referral generalization.",
        ],
    }
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    evidence = Path(metrics_path).parent
    evidence.mkdir(parents=True, exist_ok=True)
    rows = []
    for task in ("route", "urgency"):
        model = make_model().fit(train.text, train[task])
        p = model.predict_proba(test.text)
        classes = list(model.classes_)
        report[task] = metrics(test[task].tolist(), p, classes)
        joblib.dump(model, out / f"{task}.joblib")
        for i, (_, row) in enumerate(test.iterrows()):
            rows.append(
                {
                    "note_sha256": hashlib.sha256(row.text.encode()).hexdigest(),
                    "task": task,
                    "true_label": row[task],
                    "predicted_label": classes[int(p[i].argmax())],
                    "probabilities": dict(zip(classes, map(float, p[i]))),
                }
            )
    (out / "VERSION").write_text("tfidf-logreg-synthetic-v2\n")
    (evidence / "predictions.jsonl").write_text(
        "".join(json.dumps(x, sort_keys=True) + "\n" for x in rows)
    )
    manifest = [
        {"note_sha256": hashlib.sha256(row.text.encode()).hexdigest(), "split": split}
        for split, data_frame in (("train", train), ("test", test))
        for _, row in data_frame.iterrows()
    ]
    (evidence / "split_manifest.json").write_text(json.dumps(manifest, indent=2))
    report["model_sha256"] = {
        name: hashlib.sha256((out / name).read_bytes()).hexdigest()
        for name in ("route.joblib", "urgency.joblib", "VERSION")
    }
    report["environment"] = {
        k: importlib.metadata.version(k) for k in ["numpy", "pandas", "scikit-learn", "joblib"]
    }
    Path(metrics_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic_referrals.csv")
    ap.add_argument("--output", default="models/baseline")
    ap.add_argument("--metrics", default="artifacts/baseline_metrics.json")
    a = ap.parse_args()
    print(json.dumps(benchmark(a.data, a.output, a.metrics), indent=2))


if __name__ == "__main__":
    main()
