from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd

ROUTES = {
    "otology": {
        "symptoms": ["ear pain", "ear discharge", "blocked ear"],
        "findings": ["inflamed tympanic membrane", "middle ear effusion"],
    },
    "audiology": {
        "symptoms": ["gradual hearing loss", "tinnitus"],
        "findings": ["failed hearing screen", "reduced hearing threshold"],
    },
    "rhinology": {
        "symptoms": ["nasal obstruction", "sinus pressure"],
        "findings": ["deviated nasal septum", "nasal polyp"],
    },
    "laryngology": {
        "symptoms": ["persistent hoarseness", "voice fatigue"],
        "findings": ["persistent dysphonia", "swallowing concern"],
    },
    "general_ent": {
        "symptoms": ["neck swelling", "sore throat"],
        "findings": ["recurrent tonsillitis", "persistent throat symptoms"],
    },
}

URGENCIES = {
    "routine": ["routine specialist review is requested"],
    "expedited": ["earlier specialist review is requested"],
    "urgent": ["urgent assessment is requested"],
}


def generate(n: int, seed: int) -> pd.DataFrame:
    # Deterministic pseudo-randomness is intentional here: this generator creates
    # reproducible synthetic test fixtures and is not used for security decisions.
    rng = random.Random(seed)  # nosec B311
    routes = list(ROUTES)
    urgencies = list(URGENCIES)
    rows: list[dict[str, object]] = []

    for idx in range(n):
        route = routes[idx % len(routes)]
        urgency = urgencies[(idx // len(routes)) % len(urgencies)]
        symptom = rng.choice(ROUTES[route]["symptoms"])
        finding = rng.choice(ROUTES[route]["findings"])
        duration = rng.choice(["3 days", "1 week", "2 weeks", "6 weeks", "3 months"])
        email = f"synthetic.patient{idx}@example.test"
        phone = f"+91-90000-{idx % 100000:05d}"
        mrn = f"SYN-{100000 + idx}"
        text = (
            f"ENT referral for {symptom} for {duration}. Finding: {finding}. "
            f"{URGENCIES[urgency][0]}. Contact {email}; phone {phone}; MRN {mrn}."
        )
        rows.append(
            {
                "note_id": f"SYN-{idx:05d}",
                "text": text,
                "route": route,
                "urgency": urgency,
                "synthetic": True,
            }
        )

    rng.shuffle(rows)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/synthetic_referrals.csv")
    args = parser.parse_args()

    frame = generate(args.rows, args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    print(f"Wrote {len(frame)} synthetic records to {output}")


if __name__ == "__main__":
    main()
