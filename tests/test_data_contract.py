from scripts.check_data_contract import validate


def test_repository_synthetic_data_contract():
    assert validate("data/synthetic_referrals.csv") == []
