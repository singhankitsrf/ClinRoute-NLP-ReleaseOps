from __future__ import annotations
from typing import Literal
from pydantic import BaseModel,Field
Route=Literal["otology","audiology","rhinology","laryngology","general_ent"]; Urgency=Literal["routine","expedited","urgent"]
class AnalyzeRequest(BaseModel): text:str=Field(min_length=3,max_length=12000)
class Entity(BaseModel): type:str; value:str; start:int; end:int
class AnalyzeResponse(BaseModel):
    route:str; route_confidence:float; urgency:str; urgency_confidence:float; review_required:bool; redacted_text:str; entities:list[Entity]; model_version:str; disclaimer:str="Research/engineering output; not a clinical diagnosis."
