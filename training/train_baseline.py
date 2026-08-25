from __future__ import annotations
import argparse,json
from pathlib import Path
import joblib,pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from clinroute.calibration import expected_calibration_error
def make_model(): return Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=30000,sublinear_tf=True)),("clf",LogisticRegression(max_iter=1500,class_weight="balanced"))])
def metrics(y_true,probs,classes):
    pred_idx=probs.argmax(axis=1); pred=[classes[i] for i in pred_idx]; class_to_idx={c:i for i,c in enumerate(classes)}; encoded=[class_to_idx[x] for x in y_true]; return {"accuracy":float(accuracy_score(y_true,pred)),"macro_f1":float(f1_score(y_true,pred,average="macro")),"ece":expected_calibration_error(encoded,probs)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",default="data/synthetic_referrals.csv"); ap.add_argument("--output",default="models/baseline"); ap.add_argument("--metrics",default="artifacts/baseline_metrics.json"); a=ap.parse_args(); frame=pd.read_csv(a.data); train,test=train_test_split(frame,test_size=0.20,random_state=42,stratify=frame["route"].astype(str)+"::"+frame["urgency"].astype(str)); route_model=make_model(); urgency_model=make_model(); route_model.fit(train["text"],train["route"]); urgency_model.fit(train["text"],train["urgency"]); rp=route_model.predict_proba(test["text"]); up=urgency_model.predict_proba(test["text"]); report={"benchmark_scope":"synthetic_data_only","test_samples":int(len(test)),"route":metrics(test["route"].tolist(),rp,list(route_model.classes_)),"urgency":metrics(test["urgency"].tolist(),up,list(urgency_model.classes_))}; out=Path(a.output); out.mkdir(parents=True,exist_ok=True); joblib.dump(route_model,out/"route.joblib"); joblib.dump(urgency_model,out/"urgency.joblib"); (out/"VERSION").write_text("tfidf-logreg-synthetic-v1\n"); mp=Path(a.metrics); mp.parent.mkdir(parents=True,exist_ok=True); mp.write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
if __name__=="__main__": main()
