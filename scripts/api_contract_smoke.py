from clinroute.entities import extract_entities
from clinroute.redaction import redact_obvious_identifiers


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    text = (
        "Referral for ear pain for 2 weeks. Contact demo.person@example.test. "
        "Phone +91-90000-12345. MRN SYN-123456."
    )
    redacted = redact_obvious_identifiers(text)
    entities = extract_entities(redacted)

    _require("[EMAIL_REDACTED]" in redacted, "email redaction contract failed")
    _require("[PHONE_REDACTED]" in redacted, "phone redaction contract failed")
    _require("[MRN_REDACTED]" in redacted, "MRN redaction contract failed")
    _require(any(e.type == "SYMPTOM" for e in entities), "symptom extraction contract failed")
    _require(any(e.type == "DURATION" for e in entities), "duration extraction contract failed")
    print("API/NLP smoke contract: PASS")


if __name__ == "__main__":
    main()
