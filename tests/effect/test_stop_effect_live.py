from openai_chat_compat_tester.test_support import literal_echo_request, response_text


def test_stop_effect(live_client, model_name, turn_mode):
    baseline = literal_echo_request(live_client, model_name, turn_mode=turn_mode)
    full_text = response_text(baseline).strip()
    assert "<END>" in full_text and "omega" in full_text

    stopped = literal_echo_request(
        live_client, model_name, turn_mode=turn_mode, stop=["<END>"]
    )
    cut_text = response_text(stopped).strip()

    assert cut_text.lower() == "alpha"
    assert "<end>" not in cut_text.lower()
    assert "omega" not in cut_text.lower()
    assert stopped.choices[0].finish_reason == "stop"
