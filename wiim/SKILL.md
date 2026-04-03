---
name: wiim
description: Control WiiM audio player and play Tidal music natively. Use when user wants to play music, control playback, adjust volume, or discover WiiM devices. Supports playing Tidal songs, albums, artists, and playlists at full Hi-Res quality.
allowed-tools: Bash
---

# WiiM Skill

Control WiiM devices and play Tidal music natively via UPnP. Run `discover` first.

All commands: `uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_cli.py --command <cmd> [options]`

`--device` accepts partial name match. Auto-selects if only one device.

## Play Tidal music (native Hi-Res)

```bash
wiim --command play-tidal --value "Eye of the Tiger"                      # Search & play track
wiim --command play-tidal --value "Claudio Arrau" --type artist           # Play artist top tracks
wiim --command play-tidal --value "Chopin Nocturnes Arrau" --type album   # Play album
wiim --command play-tidal --playlist_id "UUID"                            # Play Tidal playlist
wiim --command play-tidal --value "jazz" --limit 30                       # Search with limit
wiim --command play-tidal --value "Bach" --device "kitchen"               # Play on specific device
```

## Playback control

```bash
wiim --command status              # What's playing
wiim --command play                # Resume
wiim --command pause               # Pause
wiim --command stop                # Stop
wiim --command next                # Next track
wiim --command prev                # Previous track
wiim --command volume              # Get volume
wiim --command volume --value 50   # Set volume (0-100)
wiim --command mute                # Mute
wiim --command unmute              # Unmute
wiim --command seek --value 120    # Seek (seconds)
wiim --command loop --value shuffle # Loop: all, one, shuffle, sequential
```

## Device management

```bash
wiim --command discover            # Find WiiM devices on network
wiim --command device              # Device info (firmware, IP, etc.)
```
