#!/usr/bin/env python3
"""Transcribe audio files using faster-whisper (local, no API key needed)."""

import argparse
import sys
from pathlib import Path


def transcribe(audio_path: str, model: str = "base", language: str | None = None) -> str:
    from faster_whisper import WhisperModel

    model_instance = WhisperModel(model, device="auto", compute_type="auto")
    segments, info = model_instance.transcribe(
        audio_path,
        language=language,
        beam_size=5,
    )
    text = " ".join(seg.text.strip() for seg in segments)
    return text


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with faster-whisper")
    parser.add_argument("file", help="Path to audio file (.mp3, .ogg, .wav, .m4a, etc.)")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Language code (e.g. en, es, fr). Auto-detect if omitted.",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    text = transcribe(str(path), model=args.model, language=args.language)
    print(text)


if __name__ == "__main__":
    main()
