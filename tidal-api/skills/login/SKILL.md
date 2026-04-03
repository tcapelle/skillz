---
name: login
description: Log in to Tidal or check session status. Use when the user wants to authenticate with Tidal or verify their login.
user-invocable: true
allowed-tools:
  - Bash
---

# /tidal:login — Tidal Authentication

Session persisted at `~/.tidal/session.json`.

## Commands

```bash
# Login via browser OAuth (opens browser, prints device code)
uv run --project ${CLAUDE_SKILL_DIR}/../.. tidal --command login

# Check if session is valid
uv run --project ${CLAUDE_SKILL_DIR}/../.. tidal --command login --status
```

## Flow

1. If user wants to check status, run with `--status`.
2. If user wants to log in, run without `--status` — a browser tab opens for OAuth, device code is printed to terminal.
3. After login, session is saved and reused by all other tidal commands.
