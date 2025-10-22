import pytest

from tradingagents import risk


def make_state():
    return risk.RiskState()


def make_params():
    return risk.RiskParams(
        max_daily_loss=1_000,
        max_exposure=10_000,
        max_concentration_per_symbol=5_000,
        cooldown_bars=2,
        min_stop_distance_factor=0.5,
    )


def test_exposure_cap_triggers():
    params = make_params()
    state = make_state()
    risk.record_trade("BTC-USD", 8_000, state)
    with pytest.raises(risk.RiskRejection, match="exposure cap"):
        risk.check_trade(3_000, "ETH-USD", atr_14=5, stop_distance=5, params=params, state=state)


def test_concentration_cap_triggers():
    params = make_params()
    state = make_state()
    risk.record_trade("BTC-USD", 4_000, state)
    with pytest.raises(risk.RiskRejection, match="concentration cap"):
        risk.check_trade(2_000, "BTC-USD", atr_14=5, stop_distance=5, params=params, state=state)


def test_stop_distance_guard():
    params = make_params()
    state = make_state()
    with pytest.raises(risk.RiskRejection, match="stop too tight"):
        risk.check_trade(1_000, "BTC-USD", atr_14=4, stop_distance=0.5, params=params, state=state)


def test_cooldown_after_loss_blocks_trades():
    params = make_params()
    state = make_state()
    risk.record_daily_pnl(-2_000, params, state)
    with pytest.raises(risk.RiskRejection, match="cooldown"):
        risk.check_trade(1_000, "BTC-USD", atr_14=5, stop_distance=5, params=params, state=state)
    state.decay_cooldown()
    with pytest.raises(risk.RiskRejection, match="cooldown"):
        risk.check_trade(1_000, "BTC-USD", atr_14=5, stop_distance=5, params=params, state=state)
    state.decay_cooldown()
    risk.check_trade(1_000, "BTC-USD", atr_14=5, stop_distance=5, params=params, state=state)
