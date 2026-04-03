---
name: tidal-api
description: Interact with Tidal music service — search catalog, manage playlists, get favorites and recommendations. Use when user asks about their Tidal music, wants to find songs, create playlists, or get recommendations.
allowed-tools: Bash
---

# Tidal API Skill

Interact with the user's Tidal account via CLI scripts. All scripts use `tidalapi` directly — no server needed.

Session is persisted at `~/.tidal/session.json`. If expired, scripts auto-open the browser for OAuth login.

## Running scripts

All scripts live in `${CLAUDE_SKILL_DIR}`. Run them with:

```bash
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/<script>.py <args>
```

## Scripts reference

### tidal_auth.py — Authentication

```bash
# Login (opens browser if needed)
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_auth.py

# Check session status
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_auth.py --status
```

### tidal_search.py — Search catalog

```bash
# Search everything
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_search.py --query "Beatles"

# Search specific type: tracks, albums, artists, playlists
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_search.py --query "Radiohead" --type artists

# With limit
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_search.py --query "jazz" --type tracks --limit 10
```

Output is JSON with track/album/artist/playlist objects including IDs and Tidal URLs.

### tidal_playlists.py — Playlist management

```bash
# List all playlists
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action list

# Get tracks from a playlist
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action tracks --playlist_id "UUID"

# Create playlist with tracks
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action create --title "My Playlist" --track_ids "123,456,789" --description "Optional desc"

# Add tracks to existing playlist
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action add --playlist_id "UUID" --track_ids "123,456"

# Remove tracks by ID or by 0-based index
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action remove --playlist_id "UUID" --track_ids "123"
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action remove --playlist_id "UUID" --indices "0,3,5"

# Update title/description
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action update --playlist_id "UUID" --title "New Name"

# Reorder: move track from position A to position B (0-based)
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action reorder --playlist_id "UUID" --from_index 5 --to_index 0

# Delete playlist
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_playlists.py --action delete --playlist_id "UUID"
```

### tidal_tracks.py — Favorites and recommendations

```bash
# Get favorite tracks
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_tracks.py --action favorites --limit 30

# Get recommendations from specific tracks
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_tracks.py --action recommend --track_ids "123,456" --limit 20

# Get recommendations from favorites (auto-uses favorites as seeds)
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/tidal_tracks.py --action recommend --limit_seeds 10 --limit 20
```

## Workflow tips

- **Creating a playlist from recommendations**: First run `tidal_tracks.py recommend`, pick track IDs from the output, then run `tidal_playlists.py create` with those IDs.
- **Finding tracks to add**: Use `tidal_search.py` to find track IDs, then `tidal_playlists.py add`.
- **Naming playlists**: Check existing playlists with `tidal_playlists.py list` first to match the user's naming style.
- All data output is JSON — extract IDs directly for follow-up operations.
- Tidal URLs are included in all results so users can open tracks/playlists directly.
