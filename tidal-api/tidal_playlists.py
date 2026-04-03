import json
from dataclasses import dataclass

import simple_parsing as sp
from rich.console import Console

from tidal_session import get_session, fetch_all_items, format_track

console = Console()


@dataclass
class Args:
    """Tidal playlist management"""
    action: str                # list, create, delete, tracks, add, remove, update, reorder
    playlist_id: str = ""      # Playlist ID (required for most actions)
    title: str = ""            # Playlist title (create/update)
    description: str = ""      # Playlist description (create/update)
    track_ids: str = ""        # Comma-separated track IDs (create/add/remove)
    indices: str = ""          # Comma-separated 0-based indices (remove)
    from_index: int = -1       # Source position (reorder)
    to_index: int = -1         # Target position (reorder)
    limit: int = 0             # Max tracks to fetch, 0 = all (tracks)


def parse_ids(s: str) -> list[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


args = sp.parse(Args)
session = get_session()

match args.action:
    case "list":
        playlists = session.user.playlists()
        output = [
            {
                "id": p.id,
                "title": p.name,
                "description": p.description or "",
                "track_count": p.num_tracks,
                "duration": p.duration,
                "last_updated": str(p.last_updated) if p.last_updated else None,
                "url": f"https://tidal.com/playlist/{p.id}",
            }
            for p in playlists
        ]
        console.print_json(json.dumps(output, default=str))

    case "create":
        track_ids = parse_ids(args.track_ids)
        playlist = session.user.create_playlist(args.title, args.description)
        if track_ids:
            playlist.add(track_ids)
        console.print_json(json.dumps({
            "id": playlist.id,
            "title": playlist.name,
            "tracks_added": len(track_ids),
            "url": f"https://tidal.com/playlist/{playlist.id}",
        }))

    case "delete":
        playlist = session.playlist(args.playlist_id)
        playlist.delete()
        console.print(f"[green]Deleted playlist {args.playlist_id}[/green]")

    case "tracks":
        playlist = session.playlist(args.playlist_id)
        limit = args.limit if args.limit > 0 else None

        def fetch_page(limit, offset):
            try:
                return list(playlist.items(limit=limit, offset=offset))
            except TypeError:
                return list(playlist.items(limit=limit)) if offset == 0 else []

        tracks = fetch_all_items(fetch_page, max_items=limit)
        output = {
            "playlist_id": playlist.id,
            "playlist_title": playlist.name,
            "total_tracks": len(tracks),
            "tracks": [format_track(t) for t in tracks],
        }
        console.print_json(json.dumps(output, default=str))

    case "add":
        track_ids = parse_ids(args.track_ids)
        playlist = session.playlist(args.playlist_id)
        playlist.add(track_ids)
        console.print(f"[green]Added {len(track_ids)} track(s) to {args.playlist_id}[/green]")

    case "remove":
        playlist = session.playlist(args.playlist_id)
        if args.track_ids:
            for tid in parse_ids(args.track_ids):
                playlist.remove_by_id(tid)
        elif args.indices:
            for idx in sorted([int(i) for i in parse_ids(args.indices)], reverse=True):
                playlist.remove_by_index(idx)
        console.print(f"[green]Removed tracks from {args.playlist_id}[/green]")

    case "update":
        playlist = session.playlist(args.playlist_id)
        playlist.edit(
            title=args.title or None,
            description=args.description or None,
        )
        console.print(f"[green]Updated playlist {args.playlist_id}[/green]")

    case "reorder":
        playlist = session.playlist(args.playlist_id)
        playlist.move(args.from_index, args.to_index)
        console.print(f"[green]Moved track from {args.from_index} to {args.to_index}[/green]")

    case _:
        console.print(f"[red]Unknown action: {args.action}. Use: list, create, delete, tracks, add, remove, update, reorder[/red]")
