---
name: search
description: Search the Tidal music catalog for tracks, albums, artists, or playlists. Use when the user wants to find music on Tidal.
user-invocable: true
allowed-tools:
  - Bash
---

# /tidal:search — Search Tidal Catalog

All commands: `tidal --command search [options]`

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--query` | required | Search query |
| `--type` | `all` | `all`, `tracks`, `albums`, `artists`, `playlists` |
| `--limit` | `20` | Max results |

## Examples

```bash
tidal --command search --query "Beatles"
tidal --command search --query "Radiohead" --type artists
tidal --command search --query "jazz" --limit 10
```

## Tips

- Output is JSON with IDs and Tidal URLs — extract IDs for playlist or playback operations.
- Use `--type` to narrow results when looking for a specific kind of content.
