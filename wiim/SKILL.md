---
name: wiim
description: Control WiiM audio player on the local network — playback, volume, now playing, device info. Use when the user wants to control their WiiM speaker, check what's playing, or adjust volume.
allowed-tools: Bash
---

# WiiM Skill

Control the user's WiiM audio player via its local HTTPS API. No cloud, no auth — direct local network control.

Default device: `Cape-Wiim.local` (override with `--host`).

## Running scripts

All scripts live in `${CLAUDE_SKILL_DIR}`. Run them with:

```bash
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/<script>.py <args>
```

## Scripts reference

### wiim_status.py — Now playing and device info

```bash
# What's currently playing?
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_status.py --action now_playing

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

# Play a direct audio URL
uv run --project ${CLAUDE_SKILL_DIR} ${CLAUDE_SKILL_DIR}/wiim_control.py --action play_url --value "http://example.com/stream.mp3"
```

## Tips

- The `now_playing` command shows current track, source (Qobuz, Tidal, AirPlay, Bluetooth, etc.), position, volume, and mute state.
- Volume is 0-100. The WiiM has no soft volume limiting — be careful at high values.
- The `play_url` action can stream any audio URL directly to the WiiM — useful for combining with the tidal-api skill to push Tidal streams.
- All metadata (title, artist, album) is automatically decoded from the WiiM's hex encoding.
