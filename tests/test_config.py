from config import Settings

def test_default_settings():
    settings = Settings()
    assert settings.base_weekly_budget == 1000.0
    assert settings.min_multiplier == 0.5
    assert settings.max_multiplier == 2.0
    assert "100.105.249.12:4000" in settings.llm_gateway_url
    assert settings.llm_model == "auto"
