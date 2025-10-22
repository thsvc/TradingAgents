import tradingagents.policy as policy


def test_position_size_caps_at_max_notional():
    params = policy.PolicyParams(k=0.5, max_notional=50_000)
    size = policy.position_size(atr_14=10, equity=1_000_000, params=params)
    assert size == 50_000


def test_should_trade_respects_vol_and_spread():
    params = policy.PolicyParams(min_vol=1.0, max_spread_ratio=0.5)
    ok, reason = policy.should_trade(atr_14=0.2, spread=0.01, params=params)
    assert not ok
    assert reason == "low_vol"

    ok, reason = policy.should_trade(atr_14=2.0, spread=2.0, params=params)
    assert not ok
    assert reason == "wide_spread"

    ok, reason = policy.should_trade(atr_14=2.0, spread=0.5, params=params)
    assert ok
    assert reason == ""
