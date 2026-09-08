from scripts.model_regression_gate import gate


def test_nan_and_missing_metrics_cannot_pass():
    baseline = {task: {"macro_f1": 0.9, "ece": 0.1} for task in ("route", "urgency")}
    candidate = {task: {"macro_f1": float("nan"), "ece": 0.1} for task in baseline}
    assert gate(candidate, baseline)
    assert gate({}, baseline)


def test_changed_evaluation_corpus_cannot_pass():
    baseline = {task: {"macro_f1": 0.9, "ece": 0.1} for task in ("route", "urgency")}
    baseline["normalized_corpus_sha256"] = "old"
    assert gate({**baseline, "normalized_corpus_sha256": "new"}, baseline)
