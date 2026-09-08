from __future__ import annotations
import argparse, sys, pandas as pd

REQUIRED = {"note_id", "text", "route", "urgency", "synthetic"}
ROUTES = {"otology", "audiology", "rhinology", "laryngology", "general_ent"}
URGENCIES = {"routine", "expedited", "urgent"}


def validate(path: str) -> list[str]:
    frame = pd.read_csv(path)
    errors = []
    missing = REQUIRED - set(frame.columns)
    if missing:
        return [f"Missing columns: {sorted(missing)}"]
    if frame["note_id"].duplicated().any():
        errors.append("Duplicate note_id values found.")
    if frame["text"].duplicated().any():
        errors.append("Duplicate text records found.")
    if not set(frame["route"].unique()) <= ROUTES:
        errors.append("Unknown route label found.")
    if not set(frame["urgency"].unique()) <= URGENCIES:
        errors.append("Unknown urgency label found.")
    if frame["text"].fillna("").str.len().lt(10).any():
        errors.append("Text shorter than 10 characters found.")
    if not frame["synthetic"].astype(bool).all():
        errors.append("Repository training data must be marked synthetic.")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic_referrals.csv")
    a = ap.parse_args()
    errors = validate(a.data)
    if errors:
        [print("ERROR:", e) for e in errors]
        sys.exit(1)
    print("Data contract: PASS")


if __name__ == "__main__":
    main()
