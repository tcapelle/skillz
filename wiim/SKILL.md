---
name: wiim
description: Control WiiM audio player on the local network — playback, volume, now playing, device info. Use when the user wants to control their WiiM speaker, check what's playing, or adjust volume.
allowed-tools: Bash
---

# WiiM Skill

Control the user's WiiM audio player(s) via local HTTPS API. No cloud, no auth — direct local network control.

## Setup

Run discovery first to find devices on the network:

```bash
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_discover.py
```

This scans for WiiM devices and caches them in `~/.wiim/devices.json`. Re-run if devices change IP.

## Device selection

All scripts accept `--device` to target a specific WiiM by name (partial match, case-insensitive):

```bash
--device "Cape Wiim"    # exact match
--device "cape"         # partial match
--device "kitchen"      # matches "Kitchen WiiM"
```

If only one device exists, it's auto-selected (no `--device` needed).

## Running scripts

```bash
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/<script>.py <args>
```

## Scripts reference

### wiim_discover.py — Find devices on the network

```bash
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_discover.py
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_discover.py --timeout 10
```

### wiim_status.py — Now playing and device info

```bash
# What's currently playing?
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_status.py --action now_playing

# What's playing on a specific device?
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_status.py --action now_playing --device "kitchen"

# Device info (firmware, IP, WiFi, etc.)
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_status.py --action device
```

### wiim_control.py — Playback control

```bash
# Play / pause / toggle / stop
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action play
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action pause
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action toggle
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action stop

# Next / previous track
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action next
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action prev

# Volume (0-100) — get or set
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action volume
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action volume --value 50

# Mute / unmute
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action mute
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action unmute

# Seek to position (seconds)
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action seek --value 120

# Loop mode: all, one, shuffle_loop, shuffle, sequential
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action loop --value shuffle

# Play a direct audio URL on a specific device
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action play_url --value "http://example.com/stream.mp3" --device "living room"
```

## Tips

- Run `wiim_discover.py` on first use and whenever devices change IP.
- The `now_playing` command shows current track, source (Qobuz, Tidal, AirPlay, Bluetooth, etc.), position, volume, and mute state.
- Volume is 0-100. The WiiM has no soft volume limiting — be careful at high values.
- The `play_url` action can stream any audio URL directly to the WiiM.
- All metadata (title, artist, album) is automatically decoded from the WiiM's hex encoding.
