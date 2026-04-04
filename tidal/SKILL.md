---
name: tidal
description: Interact with Tidal music service — search catalog, manage playlists, get favorites and recommendations. Use when user asks about their Tidal music, wants to find songs, create playlists, or get recommendations.
allowed-tools: Bash
---

# Tidal API Skill

Interact with Tidal via CLI. Session persisted at `~/.tidal/session.json`.

All commands: `uv run ${CLAUDE_SKILL_DIR}/tidal_cli.py <command> [options]`

## Commands

```bash
# Auth
tidal_cli.py login                                     # Login via browser OAuth
tidal_cli.py login --status                            # Check session

# Search (JSON output with IDs and Tidal URLs)
tidal_cli.py search --query "Beatles"                  # Search everything
tidal_cli.py search --query "Radiohead" --type artists # tracks, albums, artists, playlists
tidal_cli.py search --query "jazz" --limit 10

# Favorites & recommendations
tidal_cli.py favorites --limit 30
tidal_cli.py recommend --track_ids "123,456" --limit 20        # From specific tracks
tidal_cli.py recommend --limit_seeds 10 --limit 20             # From favorites

# Playlists
tidal_cli.py playlists                                          # List all
tidal_cli.py playlist-tracks --playlist_id UUID --limit 0       # Get tracks (0=all)
tidal_cli.py playlist-create --title "Name" --track_ids "1,2,3" --description ""
tidal_cli.py playlist-add --playlist_id UUID --track_ids "1,2"
tidal_cli.py playlist-remove --playlist_id UUID --track_ids "1" # Or --indices "0,3"
tidal_cli.py playlist-update --playlist_id UUID --title "New"
tidal_cli.py playlist-reorder --playlist_id UUID --from_index 5 --to_index 0
tidal_cli.py playlist-delete --playlist_id UUID
```

## Tips

- All data output is JSON — extract IDs for follow-up operations.
- Check existing playlists with `tidal playlists` first to match user's naming style.
- Tidal URLs included in all results so users can open content directly.
