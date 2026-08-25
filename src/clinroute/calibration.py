from __future__ import annotations
import numpy as np
def expected_calibration_error(y_true,probabilities,bins:int=15)->float:
    y_true=np.asarray(y_true); p=np.asarray(probabilities); confidence=p.max(axis=1); prediction=p.argmax(axis=1); correct=(prediction==y_true).astype(float); edges=np.linspace(0.0,1.0,bins+1); ece=0.0
    for lo,hi in zip(edges[:-1],edges[1:]):
        mask=(confidence>lo)&(confidence<=hi)
        if mask.any(): ece+=mask.mean()*abs(correct[mask].mean()-confidence[mask].mean())
    return float(ece)
