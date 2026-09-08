"""Fail closed when metrics are missing, non-finite, or regressed."""

from __future__ import annotations
import argparse
import json
import math
import sys


def gate(candidate: dict, baseline: dict, f1_tolerance: float = 0.01, ece_tolerance: float = 0.02):
    failures = []
    for key in ("benchmark_scope", "protocol", "normalized_corpus_sha256"):
        if key in baseline and candidate.get(key) != baseline[key]:
            failures.append(f"{key} mismatch")
    for task in ("route", "urgency"):
        try:
            c, b = candidate[task], baseline[task]
            for item in (c, b):
                for key in ("macro_f1", "ece"):
                    value = float(item[key])
                    if not math.isfinite(value) or not 0 <= value <= 1:
                        raise ValueError("invalid metric")
            if c["macro_f1"] < b["macro_f1"] - f1_tolerance:
                failures.append(f"{task} macro_f1 regressed")
            if c["ece"] > b["ece"] + ece_tolerance:
                failures.append(f"{task} ECE regressed")
        except (KeyError, TypeError, ValueError):
            failures.append(f"{task} missing or invalid metrics")
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--f1-tolerance", type=float, default=0.01)
    ap.add_argument("--ece-tolerance", type=float, default=0.02)
    a = ap.parse_args()
    failures = gate(
        json.loads(open(a.candidate).read()),
        json.loads(open(a.baseline).read()),
        a.f1_tolerance,
        a.ece_tolerance,
    )
    if failures:
        print("MODEL REGRESSION GATE: FAIL", *failures, sep="\n")
        sys.exit(1)
    print("MODEL REGRESSION GATE: PASS")


if __name__ == "__main__":
    main()
