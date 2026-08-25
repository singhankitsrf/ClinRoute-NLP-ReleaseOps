from __future__ import annotations
import re
from dataclasses import dataclass
@dataclass(frozen=True)
class ExtractedEntity:
    type:str; value:str; start:int; end:int
LEXICON={"SYMPTOM":["ear pain","ear discharge","blocked ear","hearing loss","hearing difficulty","tinnitus","nasal obstruction","sinus pressure","reduced smell","persistent nasal discharge","hoarseness","voice fatigue","difficulty swallowing","neck swelling","sore throat","tonsil concern"],"FINDING":["inflamed tympanic membrane","perforated tympanic membrane","middle ear effusion","retracted tympanic membrane","deviated nasal septum","nasal polyp","recurrent tonsillitis","persistent dysphonia"]}
DURATION=re.compile(r"\b(?:for\s+)?\d+\s*(?:day|days|week|weeks|month|months|year|years)\b",re.I)
def extract_entities(text:str)->list[ExtractedEntity]:
    found=[]; lower=text.lower()
    for typ,terms in LEXICON.items():
        for term in terms:
            start=0
            while True:
                idx=lower.find(term,start)
                if idx<0: break
                found.append(ExtractedEntity(typ,text[idx:idx+len(term)],idx,idx+len(term))); start=idx+len(term)
    for m in DURATION.finditer(text): found.append(ExtractedEntity("DURATION",m.group(0),m.start(),m.end()))
    return sorted(found,key=lambda x:(x.start,x.end))
