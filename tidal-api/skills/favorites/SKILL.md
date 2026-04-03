---
name: favorites
description: Get Tidal favorites and track recommendations. Use when user asks about their liked tracks or wants music recommendations.
user-invocable: true
allowed-tools:
  - Bash
---

# /tidal:favorites — Favorites & Recommendations

All commands: `tidal --command <cmd> [options]`

## Commands

```bash
# Get favorite tracks (most recent first)
tidal --command favorites --limit 30

# Recommend tracks from specific seeds
tidal --command recommend --track_ids "123,456" --limit 20

# Recommend from your top favorites
tidal --command recommend --limit_seeds 10 --limit 20
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--limit` | `20` | Max results |
| `--track_ids` | `""` | Comma-separated seed track IDs (recommend) |
| `--limit_seeds` | `20` | Max favorites to use as seeds (recommend) |

## Tips

- Use `favorites` first to see liked tracks, then pass IDs to `recommend` for targeted suggestions.
- Recommendations include a `seed_track_id` field so you can trace which seed generated each result.
