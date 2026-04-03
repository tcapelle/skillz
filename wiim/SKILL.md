---
name: wiim
description: Control WiiM audio player — playback, volume, now playing, device discovery. Use when user wants to control music, check what's playing, or adjust volume on their WiiM.
allowed-tools: Bash
---

# WiiM Skill

Control WiiM audio devices via local HTTPS API. Run `discover` first to find devices.

All commands: `uv run --project ${CLAUDE_SKILL_DIR} wiim <command> [value] [--device NAME]`

`--device` accepts partial name match. Auto-selects if only one device exists.

## Commands

```bash
wiim discover [--timeout 5]       # Find WiiM devices on the network
wiim status [--device NAME]       # What's currently playing
wiim device [--device NAME]       # Device info (firmware, IP, etc.)
wiim play                         # Resume playback
wiim pause                        # Pause
wiim toggle                       # Toggle play/pause
wiim stop                         # Stop
wiim next                         # Next track
wiim prev                         # Previous track
wiim volume                       # Get current volume
wiim volume 50                    # Set volume (0-100)
wiim mute                         # Mute
wiim unmute                       # Unmute
wiim seek 120                     # Seek to position (seconds)
wiim loop shuffle                 # Loop mode: all, one, shuffle, sequential
wiim play-url "http://url"        # Play a direct audio URL
```
