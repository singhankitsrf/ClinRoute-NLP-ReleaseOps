from __future__ import annotations
import argparse,json,sys
def gate(candidate:dict,baseline:dict,f1_tolerance:float=0.01,ece_tolerance:float=0.02):
    failures=[]
    for task in ("route","urgency"):
        c=candidate[task]; b=baseline[task]
        if c["macro_f1"]<b["macro_f1"]-f1_tolerance: failures.append(f"{task} macro_f1 regressed")
        if c["ece"]>b["ece"]+ece_tolerance: failures.append(f"{task} ECE regressed")
    return failures
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate",required=True); ap.add_argument("--baseline",required=True); ap.add_argument("--f1-tolerance",type=float,default=0.01); ap.add_argument("--ece-tolerance",type=float,default=0.02); a=ap.parse_args(); failures=gate(json.load(open(a.candidate)),json.load(open(a.baseline)),a.f1_tolerance,a.ece_tolerance)
    if failures: print("MODEL REGRESSION GATE: FAIL"); [print("-",x) for x in failures]; sys.exit(1)
    print("MODEL REGRESSION GATE: PASS")
if __name__=="__main__": main()
