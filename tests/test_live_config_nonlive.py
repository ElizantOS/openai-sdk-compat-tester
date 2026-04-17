from openai_sdk_compat_tester.live_config import choose_model_id, extract_model_ids


class _Model:
    def __init__(self, model_id: str):
        self.id = model_id


class _Response:
    def __init__(self, data):
        self.data = data


def test_extract_model_ids_from_mixed_response_entries():
    response = _Response([{"id": "gpt-5.4"}, _Model("gpt-5.4-mini"), {"id": ""}, {}])
    assert extract_model_ids(response) == ["gpt-5.4", "gpt-5.4-mini"]


def test_choose_model_id_prefers_explicit_advertised_model():
    selected, used_fallback = choose_model_id(
        ["gpt-5.4", "gpt-5.4-mini"], "gpt-5.4-mini"
    )
    assert selected == "gpt-5.4-mini"
    assert used_fallback is False


def test_choose_model_id_falls_back_to_first_advertised_model():
    selected, used_fallback = choose_model_id(
        ["gpt-5.4", "gpt-5.4-mini"], "gpt-5-codex"
    )
    assert selected == "gpt-5.4"
    assert used_fallback is True


def test_choose_model_id_requires_non_empty_model_list():
    try:
        choose_model_id([], "")
    except ValueError as exc:
        assert str(exc) == "router returned no models from /v1/models"
    else:
        raise AssertionError("expected ValueError for empty model list")
