---
name: transcribe
description: >
  Transcribe audio files locally using faster-whisper (no API key needed).
  Use this skill when you need to transcribe voice messages, audio files, or any speech-to-text task.
  Supports .ogg, .mp3, .wav, .m4a and other formats. Works offline.
---

# Transcribe Skill

Local speech-to-text using faster-whisper. Runs on-device, no API key required.

## Usage

```bash
uv run --project /Users/thomascapelle/skillz/transcribe /Users/thomascapelle/skillz/transcribe/transcribe_cli.py <audio_file>
```

## Options

```bash
# Transcribe with auto language detection (default model: base)
transcribe voice.ogg

# Use a larger model for better accuracy
transcribe voice.ogg --model small
transcribe voice.ogg --model medium

# Force a specific language
transcribe voice.ogg --language en
transcribe voice.ogg --language es
```

## Models (accuracy vs speed tradeoff)

| Model    | Size   | Notes                          |
|----------|--------|--------------------------------|
| tiny     | ~75MB  | Fastest, least accurate        |
| base     | ~145MB | Good balance (default)         |
| small    | ~460MB | Better accuracy                |
| medium   | ~1.5GB | High accuracy                  |
| large-v3 | ~3GB   | Best accuracy, slowest         |

Models are downloaded on first use and cached in `~/.cache/huggingface/`.

## Telegram voice messages

Voice messages from Telegram arrive as `.oga` files. Convert with ffmpeg first:

```bash
ffmpeg -i message.oga /tmp/voice.mp3 -y
uv run --project /Users/thomascapelle/skillz/transcribe /Users/thomascapelle/skillz/transcribe/transcribe_cli.py /tmp/voice.mp3
```
