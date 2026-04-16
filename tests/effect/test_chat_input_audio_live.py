import pytest
import os
from pathlib import Path

from openai_chat_compat_tester.test_support import conversation_messages
from openai_chat_compat_tester.test_support import make_audio_file_wav_base64
from openai_chat_compat_tester.test_support import response_text


DEFAULT_AUDIO_FILE = Path(__file__).resolve().parents[1] / "fixtures" / "seg_3.mp3"
DEFAULT_EXPECTED_TEXT = "AI实时读取日志,自动注入JS,截图,模拟交互。"


def _normalize_transcript(text: str) -> str:
    return text.strip().rstrip("。！？.!?")


def test_chat_input_audio(live_client, model_name, turn_mode):
    phrase = os.getenv("OPENAI_COMPAT_AUDIO_EXPECTED_TEXT", "").strip() or DEFAULT_EXPECTED_TEXT
    audio_file = os.getenv("OPENAI_COMPAT_AUDIO_FILE", "").strip() or str(DEFAULT_AUDIO_FILE)
    try:
        audio_b64 = make_audio_file_wav_base64(audio_file)
    except RuntimeError as exc:
        pytest.skip(str(exc))

    response = live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=64,
        messages=conversation_messages([
            {
                "role": "developer",
                "content": (
                    "You are a speech transcription verifier. "
                    "Reply with exactly the spoken text from the audio, preserving the original language, casing, and punctuation. "
                    "Do not add explanations."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Transcribe the spoken phrase exactly."},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": "wav",
                        },
                    },
                ],
            },
        ], turn_mode),
    )

    assert _normalize_transcript(response_text(response)) == _normalize_transcript(phrase)
