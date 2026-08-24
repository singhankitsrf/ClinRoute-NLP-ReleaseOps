from __future__ import annotations
from dataclasses import asdict
from .entities import extract_entities
from .policy import review_required
from .redaction import redact_obvious_identifiers
class NLPService:
    def __init__(self,predictor,redact:bool=True,route_min_confidence:float=0.70,urgency_min_confidence:float=0.70): self.predictor=predictor; self.redact=redact; self.route_min=route_min_confidence; self.urgency_min=urgency_min_confidence
    def analyze(self,text:str)->dict:
        cleaned=redact_obvious_identifiers(text) if self.redact else text; pred=self.predictor.predict(cleaned); pred["review_required"]=review_required(pred["route_confidence"],pred["urgency_confidence"],self.route_min,self.urgency_min); pred["redacted_text"]=cleaned; pred["entities"]=[asdict(e) for e in extract_entities(cleaned)]; pred["model_version"]=getattr(self.predictor,"version","unknown"); pred["disclaimer"]="Research/engineering output; not a clinical diagnosis."; return pred
