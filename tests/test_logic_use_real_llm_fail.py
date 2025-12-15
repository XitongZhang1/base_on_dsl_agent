import pytest
from dsl_agent import logic


def test_build_intent_service_exits_when_real_llm_missing_config(caplog):
    settings = {
        "use_real_llm": True,
        "use_stub": False,
        "api_base": "",
        "api_key": "",
        "model": "",
    }
    caplog.set_level("ERROR")
    with pytest.raises(SystemExit) as exc:
        logic._build_intent_service(settings, scenario_name="banking_scenario")
    assert "LLM configuration is incomplete" in str(exc.value)
    assert any("--use-real-llm specified" in rec.message for rec in caplog.records)
