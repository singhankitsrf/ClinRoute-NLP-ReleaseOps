from clinroute.redaction import redact_obvious_identifiers
from clinroute.entities import extract_entities
def main():
    text="Referral for ear pain for 2 weeks. Contact demo.person@example.test. Phone +91-90000-12345. MRN SYN-123456."; redacted=redact_obvious_identifiers(text); entities=extract_entities(redacted); assert "[EMAIL_REDACTED]" in redacted; assert "[PHONE_REDACTED]" in redacted; assert "[MRN_REDACTED]" in redacted; assert any(e.type=="SYMPTOM" for e in entities); assert any(e.type=="DURATION" for e in entities); print("API/NLP smoke contract: PASS")
if __name__=="__main__": main()
