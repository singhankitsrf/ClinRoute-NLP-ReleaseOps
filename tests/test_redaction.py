from clinroute.redaction import redact_obvious_identifiers


def test_redacts_demo_identifiers():
    out = redact_obvious_identifiers(
        "Email demo.person@example.test phone +91-90000-12345 MRN SYN-123456."
    )
    assert "[EMAIL_REDACTED]" in out
    assert "[PHONE_REDACTED]" in out
    assert "[MRN_REDACTED]" in out
