from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import joblib
@dataclass
class BaselineBundle:
    route_model:object; urgency_model:object; version:str="tfidf-logreg"
    @classmethod
    def load(cls,model_dir:str|Path)->"BaselineBundle":
        model_dir=Path(model_dir); return cls(route_model=joblib.load(model_dir/"route.joblib"),urgency_model=joblib.load(model_dir/"urgency.joblib"),version=(model_dir/"VERSION").read_text().strip() if (model_dir/"VERSION").exists() else "tfidf-logreg")
    def predict(self,text:str)->dict:
        route_p=self.route_model.predict_proba([text])[0]; rc=self.route_model.classes_; ri=int(route_p.argmax()); urg_p=self.urgency_model.predict_proba([text])[0]; uc=self.urgency_model.classes_; ui=int(urg_p.argmax()); return {"route":str(rc[ri]),"route_confidence":float(route_p[ri]),"urgency":str(uc[ui]),"urgency_confidence":float(urg_p[ui])}
