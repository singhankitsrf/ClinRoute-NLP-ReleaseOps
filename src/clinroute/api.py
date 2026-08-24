from __future__ import annotations
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from .baseline import BaselineBundle
from .schemas import AnalyzeRequest,AnalyzeResponse
from .service import NLPService
STATE:dict[str,object|None]={"service":None}
def build_service()->NLPService|None:
    model_dir=os.getenv("MODEL_DIR","models/baseline")
    try:
        if os.path.exists(os.path.join(model_dir,"metadata.json")):
            from .transformer_predictor import TransformerBundle
            predictor=TransformerBundle.load(model_dir)
        else: predictor=BaselineBundle.load(model_dir)
    except Exception: return None
    return NLPService(predictor,redact=os.getenv("REDACT_IDENTIFIERS","true").lower()=="true",route_min_confidence=float(os.getenv("ROUTE_MIN_CONFIDENCE","0.70")),urgency_min_confidence=float(os.getenv("URGENCY_MIN_CONFIDENCE","0.70")))
@asynccontextmanager
async def lifespan(app:FastAPI): STATE["service"]=build_service(); yield
app=FastAPI(title="ClinRoute NLP ReleaseOps API",version="0.1.0",description="NLP routing and urgency prediction with release-quality guardrails.",lifespan=lifespan)
@app.get("/health")
def health(): return {"status":"ok","model_loaded":STATE["service"] is not None}
@app.post("/analyze",response_model=AnalyzeResponse)
def analyze(payload:AnalyzeRequest):
    service=STATE["service"]
    if service is None: raise HTTPException(status_code=503,detail="Model bundle is not loaded.")
    return service.analyze(payload.text)
