---
name: playlists
description: Manage Tidal playlists — list, create, edit, reorder, delete, and manage tracks. Use when user wants to work with their Tidal playlists.
user-invocable: true
allowed-tools:
  - Bash
---

# /tidal:playlists — Playlist Management

All commands: `tidal --command <cmd> [options]`

## Commands

```bash
# List all playlists
tidal --command playlists

# Get tracks in a playlist (0=all)
tidal --command playlist-tracks --playlist_id UUID --limit 0

# Create playlist
tidal --command playlist-create --title "Name" --track_ids "1,2,3" --description ""

# Add tracks
tidal --command playlist-add --playlist_id UUID --track_ids "1,2"

# Remove tracks (by ID or 0-based index)
tidal --command playlist-remove --playlist_id UUID --track_ids "1"
tidal --command playlist-remove --playlist_id UUID --indices "0,3"

# Update metadata
tidal --command playlist-update --playlist_id UUID --title "New Name"

# Reorder
tidal --command playlist-reorder --playlist_id UUID --from_index 5 --to_index 0

# Delete
tidal --command playlist-delete --playlist_id UUID
```

## Tips

- Check existing playlists with `playlists` first to match the user's naming style.
- All output is JSON with IDs and Tidal URLs.
- Use `playlist-tracks --limit 0` to get all tracks when you need the full list.
