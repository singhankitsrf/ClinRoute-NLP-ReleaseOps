from clinroute.policy import review_required


def test_review_policy():
    assert review_required(0.60, 0.90) is True
    assert review_required(0.90, 0.60) is True
    assert review_required(0.90, 0.90) is False
