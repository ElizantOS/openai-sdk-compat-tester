#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openai_sdk_compat_tester.test_support import (
    make_audio_file_wav_base64,
    make_spoken_wav_base64,
)

DEFAULT_PHRASE = "hello audio"
DEFAULT_AUDIO_FILE = PROJECT_ROOT / "tests" / "fixtures" / "seg_3.mp3"
DEFAULT_EXPECTED_TEXT = "AI实时读取日志,自动注入JS,截图,模拟交互。"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the chat input_audio test payload into a listenable wav file."
    )
    parser.add_argument(
        "--text",
        help="Text to synthesize. Used only when not rendering the default fixture or --audio-file.",
    )
    parser.add_argument(
        "--audio-file",
        help="Existing audio file to normalize to wav, matching the test helper behavior.",
    )
    parser.add_argument(
        "--voice",
        default="Samantha",
        help="macOS say voice to use when synthesizing text.",
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "artifacts" / "chat-input-audio-sample.wav"),
        help="Destination wav path.",
    )
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Generate spoken audio from text instead of using the default seg_3.mp3 fixture.",
    )
    return parser.parse_args()


def resolve_inputs(args: argparse.Namespace) -> tuple[str, str | None]:
    audio_file = (args.audio_file or os.getenv("OPENAI_COMPAT_AUDIO_FILE", "")).strip()
    if audio_file:
        return audio_file, None

    if not args.synthesize:
        return str(DEFAULT_AUDIO_FILE), DEFAULT_EXPECTED_TEXT

    phrase = (
        args.text or os.getenv("OPENAI_COMPAT_AUDIO_EXPECTED_TEXT", "")
    ).strip() or DEFAULT_PHRASE
    return "", phrase


def main() -> int:
    args = parse_args()
    audio_file, phrase = resolve_inputs(args)

    if audio_file:
        audio_b64 = make_audio_file_wav_base64(audio_file)
        source = f"file:{Path(audio_file).expanduser()}"
    else:
        assert phrase is not None
        audio_b64 = make_spoken_wav_base64(phrase, voice=args.voice)
        source = f"text:{phrase}"

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(audio_b64))

    print(f"source={source}")
    if phrase:
        print(f"phrase={phrase}")
    print(f"output={output_path}")
    print(f"bytes={output_path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
