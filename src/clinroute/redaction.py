from __future__ import annotations
import re
_PATTERNS=[("EMAIL",re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I)),("PHONE",re.compile(r"(?<!\w)(?:\+?\d[\d\-\s]{7,}\d)(?!\w)")),("MRN",re.compile(r"\b(?:MRN[:\s-]*)?(?:SYN|MRN)[-_ ]?\d{5,12}\b",re.I))]
def redact_obvious_identifiers(text:str)->str:
    result=text
    for label,pattern in _PATTERNS: result=pattern.sub(f"[{label}_REDACTED]",result)
    return result
