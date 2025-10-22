from tradingagents.risk import RiskRejection, hard_risk_gate


def test_daily_loss():
    try:
        hard_risk_gate(1000, 0, 20000, -3000, 1000)
        assert False, "Expected daily loss breach"
    except RiskRejection:
        pass


def test_exposure_cap():
    try:
        hard_risk_gate(2000, 19000, 20000, 0, 1000)
        assert False, "Expected exposure cap breach"
    except RiskRejection:
        pass


def test_within_limits_passes():
    # Should not raise when within configured limits
    hard_risk_gate(1000, 5000, 20000, -100, 1000)
