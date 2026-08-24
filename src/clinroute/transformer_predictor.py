from __future__ import annotations
import json
from pathlib import Path
import torch
from transformers import AutoTokenizer
from .transformer_model import MultiTaskTransformer
class TransformerBundle:
    def __init__(self,model,tokenizer,route_labels,urgency_labels,max_length,version): self.model=model; self.tokenizer=tokenizer; self.route_labels=route_labels; self.urgency_labels=urgency_labels; self.max_length=max_length; self.version=version
    @classmethod
    def load(cls,model_dir:str|Path)->"TransformerBundle":
        model_dir=Path(model_dir); metadata=json.loads((model_dir/"metadata.json").read_text()); tokenizer=AutoTokenizer.from_pretrained(model_dir/"tokenizer"); model=MultiTaskTransformer(str(model_dir/"encoder"),len(metadata["route_labels"]),len(metadata["urgency_labels"])); model.load_state_dict(torch.load(model_dir/"multitask_state.pt",map_location="cpu")); model.eval(); version=(model_dir/"VERSION").read_text().strip() if (model_dir/"VERSION").exists() else "dual-head-transformer"; return cls(model,tokenizer,metadata["route_labels"],metadata["urgency_labels"],int(metadata["max_length"]),version)
    def predict(self,text:str)->dict:
        encoded=self.tokenizer(text,truncation=True,max_length=self.max_length,return_tensors="pt")
        with torch.inference_mode(): r,u=self.model(encoded["input_ids"],encoded["attention_mask"]); rp=torch.softmax(r,dim=1)[0]; up=torch.softmax(u,dim=1)[0]
        ri=int(rp.argmax()); ui=int(up.argmax()); return {"route":self.route_labels[ri],"route_confidence":float(rp[ri]),"urgency":self.urgency_labels[ui],"urgency_confidence":float(up[ui])}
