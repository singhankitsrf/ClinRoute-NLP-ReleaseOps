from scripts.model_regression_gate import gate


def metrics(f1, ece):
    return {"route": {"macro_f1": f1, "ece": ece}, "urgency": {"macro_f1": f1, "ece": ece}}


def test_gate_passes_small_change():
    assert gate(metrics(0.90, 0.08), metrics(0.90, 0.08)) == []


def test_gate_blocks_f1_regression():
    assert any(
        "macro_f1 regressed" in x
        for x in gate(metrics(0.80, 0.08), metrics(0.90, 0.08), f1_tolerance=0.01)
    )


def test_gate_blocks_calibration_regression():
    assert any(
        "ECE regressed" in x
        for x in gate(metrics(0.90, 0.20), metrics(0.90, 0.08), ece_tolerance=0.02)
    )
