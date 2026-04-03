# skillz
Small collection of local music-control skills and CLIs.
This repo currently contains two Python tools:
- `tidal-api`: a CLI for authenticating with Tidal, searching the catalog, browsing favorites, getting recommendations, and managing playlists
- `wiim`: a CLI for discovering and controlling WiiM devices, including native Tidal playback on a selected speaker
Each tool is self-contained in its own directory, with its own `pyproject.toml`, lockfile, and usage notes in `SKILL.md`.
## Repo Layout
```text
.
├── tidal-api/
│   ├── SKILL.md
│   ├── pyproject.toml
│   ├── tidal_cli.py
│   └── tidal_session.py
└── wiim/
    ├── SKILL.md
    ├── pyproject.toml
    ├── wiim_cli.py
    ├── wiim_device.py
    └── tidal_bridge.py
```
## Requirements
- Python `3.12+`
- [`uv`](https://docs.astral.sh/uv/)
- Access to a local network with a WiiM device for the `wiim` tool
- A Tidal account for `tidal-api` and Tidal playback through `wiim`
## Quick Start
Install dependencies per tool:
```bash
cd tidal-api
uv sync
cd ../wiim
uv sync
```
Run commands with `uv run --project` from the repo root, or from inside each directory.
## Tidal API
Authenticate once:
```bash
uv run --project tidal-api tidal login
```
Common commands:
```bash
uv run --project tidal-api tidal search --query "Radiohead"
uv run --project tidal-api tidal favorites --limit 20
uv run --project tidal-api tidal playlists
uv run --project tidal-api tidal recommend --limit 20
```
More examples live in `tidal-api/SKILL.md`.
## WiiM
Discover devices first:
```bash
uv run --project wiim wiim --command discover
```
Common commands:
```bash
uv run --project wiim wiim --command status
uv run --project wiim wiim --command volume --value 50
uv run --project wiim wiim --command play-tidal --value "Eye of the Tiger"
uv run --project wiim wiim --command play-tidal --value "Bach" --device "kitchen"
```
More examples live in `wiim/SKILL.md`.
## Notes
- `tidal-api` is useful on its own for search and playlist workflows
- `wiim` builds on that idea by pushing Tidal playback to a WiiM device
- The tools are intentionally lightweight and meant for local, personal automation