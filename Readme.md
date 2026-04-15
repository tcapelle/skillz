# skillz
Small collection of local Claude Code skills for music control, audio, and daily life automation.

## Skills

| Skill | Description |
|-------|-------------|
| `tidal` | Search Tidal catalog, manage playlists, get favorites and recommendations |
| `wiim` | Discover and control WiiM devices, including native Tidal playback |
| `transcribe` | Local speech-to-text via faster-whisper (no API key needed) |
| `cantine-ecole-enfants` | Manage school lunch and after-school reservations on Espace Famille Chambéry |

## Requirements
- Python `3.12+`
- [`uv`](https://docs.astral.sh/uv/)
- A Tidal account for `tidal` and Tidal playback through `wiim`
- A WiiM device on your local network for the `wiim` skill
- A compatible GPU or CPU for `transcribe` (runs locally via faster-whisper)
- Espace Citoyens credentials (env vars) for `cantine-ecole-enfants`

## Setup

Skills are symlinked into `~/.claude/skills/`:

```bash
ln -sf $(pwd)/tidal ~/.claude/skills/tidal
ln -sf $(pwd)/wiim ~/.claude/skills/wiim
ln -sf $(pwd)/transcribe ~/.claude/skills/transcribe
ln -sf $(pwd)/cantine-ecole-enfants ~/.claude/skills/cantine-ecole-enfants
```

## Tidal

Standalone uv script — no project install needed.

```bash
uv run tidal/tidal_cli.py login                          # Auth via browser OAuth
uv run tidal/tidal_cli.py search --query "Radiohead"     # Search catalog
uv run tidal/tidal_cli.py favorites --limit 20           # Recent favorites
uv run tidal/tidal_cli.py playlists                      # List playlists
uv run tidal/tidal_cli.py recommend --limit 20           # Recommendations from favorites
```

## WiiM

```bash
uv run --project wiim wiim --command discover            # Find devices
uv run --project wiim wiim --command status               # Playback status
uv run --project wiim wiim --command volume --value 50    # Set volume
uv run --project wiim wiim --command play-tidal --value "Eye of the Tiger"
```

## Transcribe

Standalone uv script — no project install needed.

```bash
uv run transcribe/transcribe_cli.py audio.mp3            # Transcribe a file
```

## Cantine École Enfants

Browser-automation skill (no CLI) — manages school lunch and périscolaire reservations on Espace Famille Chambéry via Claude Code's browser tools. Requires `ESPACE_CITOYENS_LOGIN` and `ESPACE_CITOYENS_PASSWORD` env vars.

## Repo Layout
```text
.
├── tidal/
│   ├── SKILL.md
│   └── tidal_cli.py
├── wiim/
│   ├── SKILL.md
│   ├── pyproject.toml
│   ├── wiim_cli.py
│   ├── wiim_device.py
│   └── tidal_bridge.py
├── transcribe/
│   ├── SKILL.md
│   └── transcribe_cli.py
└── cantine-ecole-enfants/
    └── SKILL.md
```

More details in each skill's `SKILL.md`.
