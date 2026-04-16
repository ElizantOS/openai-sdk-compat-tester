import base64
import json
import shutil
import subprocess
import tempfile
import wave
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


RED_SQUARE_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAF0lEQVR4nGP8z0AaYCJR/aiGUQ1DSAMAQC4BH2bjRnMAAAAASUVORK5CYII="
)
DEFAULT_RED_REMOTE_IMAGE_URL = "https://dummyimage.com/16x16/ff0000/ff0000.png"
ALLOWED_SERVICE_TIERS = {"auto", "default", "flex", "scale", "priority"}
GENERATED_OCR_TEXT = "CAT-7294"


def response_text(resp) -> str:
    content = resp.choices[0].message.content
    if content is None:
        return ""
    if isinstance(content, str):
        return content

    parts = []
    for item in content:
        if isinstance(item, dict):
            if item.get("type") in ("text", "output_text"):
                parts.append(item.get("text", ""))
        else:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
    return "".join(parts)


def _multilingual_history(turn_pairs: int) -> list[dict]:
    history: list[dict] = []
    for index in range(1, turn_pairs + 1):
        history.extend(
            [
                {
                    "role": "user",
                    "content": (
                        f"Previous context turn {index}. "
                        f"English: this is earlier context {index}. "
                        f"日本語: これは前の文脈 {index} です。 "
                        f"中文：这是之前的上下文 {index}。 "
                        "Do not answer yet; wait for the next instruction."
                    ),
                },
                {
                    "role": "assistant",
                    "content": (
                        f"Acknowledged previous context {index}. "
                        "了解しました。 "
                        "已了解。 "
                        "I will answer only the next relevant instruction."
                    ),
                },
            ]
        )
    return history


def with_multilingual_history(messages: list[dict], *, long_context: bool = False) -> list[dict]:
    history = _multilingual_history(6 if long_context else 1)

    insert_at = 0
    while insert_at < len(messages) and messages[insert_at].get("role") in {"system", "developer"}:
        insert_at += 1

    return messages[:insert_at] + history + messages[insert_at:]


def conversation_messages(messages: list[dict], turn_mode: str) -> list[dict]:
    if turn_mode == "single-turn":
        return messages
    return with_multilingual_history(messages)


def content_text_parts(content) -> list[str]:
    if content is None:
        return []
    if isinstance(content, str):
        return [content]

    parts = []
    for item in content:
        if isinstance(item, dict):
            if item.get("type") in ("text", "output_text"):
                parts.append(item.get("text", ""))
        else:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
    return parts


def make_text_image_data_url(text: str) -> str:
    font = None
    for candidate in ("DejaVuSans-Bold.ttf", "Arial.ttf", "Helvetica.ttc"):
        try:
            font = ImageFont.truetype(candidate, 120)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    width = 1200
    height = 320
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill="black", font=font)

    output = BytesIO()
    image.save(output, format="PNG")
    payload = base64.b64encode(output.getvalue()).decode()
    return f"data:image/png;base64,{payload}"


def literal_echo_request(live_client, model_name, *, turn_mode: str = "multi-turn", **extra_kwargs):
    return live_client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=20,
        messages=conversation_messages(
            [
                {
                    "role": "developer",
                    "content": (
                        "You are a strict echoer. "
                        "You must reproduce the user's ASCII text exactly, without adding, removing, or changing any characters."
                    ),
                },
                {"role": "user", "content": "alpha<END>omega"},
            ],
            turn_mode,
        ),
        **extra_kwargs,
    )


def stream_text_deltas(stream) -> list[str]:
    parts = []
    for chunk in stream:
        for choice in chunk.choices:
            delta = choice.delta.content
            if delta:
                parts.append(delta)
    return parts


def extract_error_payload(exc) -> dict:
    response = getattr(exc, "response", None)
    assert response is not None
    try:
        payload = response.json()
    except Exception:
        payload = {"raw": response.text}
    assert isinstance(payload, dict)
    return payload


def assert_error_response(exc, expected_statuses=(400, 422, 500, 502, 503, 504)) -> dict:
    response = getattr(exc, "response", None)
    assert response is not None
    assert response.status_code in expected_statuses
    payload = extract_error_payload(exc)
    assert payload
    return payload


def assert_invalid_request_response(exc, expected_statuses=(400, 422)) -> dict:
    payload = assert_error_response(exc, expected_statuses=expected_statuses)
    error = payload.get("error")
    assert isinstance(error, dict)
    return error


def looks_like_json_object(text: str) -> bool:
    stripped = text.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return False
    try:
        parsed = json.loads(stripped)
    except Exception:
        return False
    return isinstance(parsed, dict)


def make_silence_wav_base64(duration_ms: int = 600, sample_rate: int = 16000) -> str:
    sample_count = int(sample_rate * duration_ms / 1000)
    pcm = b"\x00\x00" * sample_count

    output = BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm)

    return base64.b64encode(output.getvalue()).decode()


def make_spoken_wav_base64(text: str, voice: str = "Samantha") -> str:
    say = shutil.which("say")
    afconvert = shutil.which("afconvert")
    if not say or not afconvert:
        raise RuntimeError("macOS say/afconvert are required to synthesize spoken audio for this test")

    with tempfile.TemporaryDirectory() as tmpdir:
        aiff_path = Path(tmpdir) / "speech.aiff"
        wav_path = Path(tmpdir) / "speech.wav"

        say_cmd = [say, "-v", voice, "-o", str(aiff_path), text]
        try:
            subprocess.run(say_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.run([say, "-o", str(aiff_path), text], check=True, capture_output=True)

        subprocess.run(
            [afconvert, "-f", "WAVE", "-d", "LEI16@24000", "-c", "1", str(aiff_path), str(wav_path)],
            check=True,
            capture_output=True,
        )
        return base64.b64encode(wav_path.read_bytes()).decode()


def make_audio_file_wav_base64(path: str) -> str:
    afconvert = shutil.which("afconvert")
    source_path = Path(path).expanduser()
    if not source_path.is_file():
        raise RuntimeError(f"audio file not found: {source_path}")
    if source_path.suffix.lower() in {".wav", ".wave"}:
        return base64.b64encode(source_path.read_bytes()).decode()
    if not afconvert:
        raise RuntimeError("afconvert is required to normalize non-wav audio files for this test")

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "normalized.wav"
        subprocess.run(
            [afconvert, "-f", "WAVE", "-d", "LEI16@24000", "-c", "1", str(source_path), str(wav_path)],
            check=True,
            capture_output=True,
        )
        return base64.b64encode(wav_path.read_bytes()).decode()
