import json
import concurrent.futures
from dataclasses import dataclass

import simple_parsing as sp
import tidalapi
from rich.console import Console
from rich.panel import Panel
from tidalapi.user import ItemOrder, OrderDirection

from tidal_session import (
    get_session,
    load_session,
    login,
    fetch_all_items,
    format_track,
    format_album,
    format_artist,
    format_playlist,
)

console = Console()

MODEL_MAP = {
    "tracks": [tidalapi.Track],
    "albums": [tidalapi.Album],
    "artists": [tidalapi.Artist],
    "playlists": [tidalapi.Playlist],
}


@dataclass
class Args:
    """Tidal music service CLI"""
    command: str                # login, search, favorites, recommend, playlists, playlist-tracks, playlist-create, playlist-delete, playlist-add, playlist-remove, playlist-update, playlist-reorder
    query: str = ""             # Search query
    type: str = "all"           # Search type: all, tracks, albums, artists, playlists
    limit: int = 20             # Max results
    status: bool = False        # For login: check session status only
    playlist_id: str = ""       # Playlist ID
    title: str = ""             # Playlist title (create/update)
    description: str = ""       # Playlist description (create/update)
    track_ids: str = ""         # Comma-separated track IDs
    indices: str = ""           # Comma-separated 0-based indices (remove)
    from_index: int = -1        # Source position (reorder)
    to_index: int = -1          # Target position (reorder)
    limit_seeds: int = 20       # Max favorites to use as recommendation seeds


def parse_ids(s: str) -> list[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def fetch_favorites(session, limit):
    favorites = session.user.favorites
    def fetch_page(limit, offset):
        try:
            return list(favorites.tracks(limit=limit, offset=offset, order=ItemOrder.Date, order_direction=OrderDirection.Descending))
        except TypeError:
            return list(favorites.tracks(limit=limit, order=ItemOrder.Date, order_direction=OrderDirection.Descending)) if offset == 0 else []
    return fetch_all_items(fetch_page, max_items=limit)


def main():
    args = sp.parse(Args)

    # Login doesn't need an active session
    if args.command == "login":
        if args.status:
            session = load_session()
            if session:
                console.print(Panel(f"User ID: {session.user.id}", title="Tidal Session Active", style="green"))
            else:
                console.print("[red]No valid session. Run `tidal login` to authenticate.[/red]")
        else:
            session = login()
            console.print(f"[green]Logged in. User ID: {session.user.id}[/green]")
        return

    session = get_session()

    match args.command:
        case "search":
            models = MODEL_MAP.get(args.type)
            results = session.search(args.query, models=models, limit=args.limit)
            output = {"query": args.query, "type": args.type}
            if results.get("tracks") and args.type in ("all", "tracks"):
                output["tracks"] = [format_track(t) for t in results["tracks"][:args.limit]]
            if results.get("albums") and args.type in ("all", "albums"):
                output["albums"] = [format_album(a) for a in results["albums"][:args.limit]]
            if results.get("artists") and args.type in ("all", "artists"):
                output["artists"] = [format_artist(a) for a in results["artists"][:args.limit]]
            if results.get("playlists") and args.type in ("all", "playlists"):
                output["playlists"] = [format_playlist(p) for p in results["playlists"][:args.limit]]
            console.print_json(json.dumps(output, default=str))

        case "favorites":
            tracks = fetch_favorites(session, args.limit)
            console.print_json(json.dumps([format_track(t) for t in tracks], default=str))

        case "recommend":
            seed_ids = parse_ids(args.track_ids)
            if not seed_ids:
                fav_tracks = fetch_favorites(session, args.limit_seeds)
                seed_ids = [str(t.id) for t in fav_tracks]

            limit_per = min(args.limit, 50)
            seen = set()
            all_recs = []

            def get_recs(track_id: str) -> list[dict]:
                track = session.track(track_id)
                recs = track.get_track_radio(limit=limit_per)
                return [format_track(r) | {"seed_track_id": track_id} for r in recs]

            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(seed_ids), 10)) as executor:
                futures = {executor.submit(get_recs, tid): tid for tid in seed_ids}
                for future in concurrent.futures.as_completed(futures):
                    for rec in future.result():
                        if rec["id"] not in seen:
                            seen.add(rec["id"])
                            all_recs.append(rec)

            console.print_json(json.dumps({"seed_count": len(seed_ids), "recommendations": all_recs}, default=str))

        case "playlists":
            playlists = session.user.playlists()
            output = [
                {
                    "id": p.id, "title": p.name, "description": p.description or "",
                    "track_count": p.num_tracks, "duration": p.duration,
                    "last_updated": str(p.last_updated) if p.last_updated else None,
                    "url": f"https://tidal.com/playlist/{p.id}",
                }
                for p in playlists
            ]
            console.print_json(json.dumps(output, default=str))

        case "playlist-tracks":
            playlist = session.playlist(args.playlist_id)
            limit = args.limit if args.limit > 0 else None
            def fetch_page(limit, offset):
                try:
                    return list(playlist.items(limit=limit, offset=offset))
                except TypeError:
                    return list(playlist.items(limit=limit)) if offset == 0 else []
            tracks = fetch_all_items(fetch_page, max_items=limit)
            console.print_json(json.dumps({
                "playlist_id": playlist.id, "playlist_title": playlist.name,
                "total_tracks": len(tracks), "tracks": [format_track(t) for t in tracks],
            }, default=str))

        case "playlist-create":
            track_ids = parse_ids(args.track_ids)
            playlist = session.user.create_playlist(args.title, args.description)
            if track_ids:
                playlist.add(track_ids)
            console.print_json(json.dumps({
                "id": playlist.id, "title": playlist.name,
                "tracks_added": len(track_ids), "url": f"https://tidal.com/playlist/{playlist.id}",
            }))

        case "playlist-delete":
            session.playlist(args.playlist_id).delete()
            console.print(f"[green]Deleted playlist {args.playlist_id}[/green]")

        case "playlist-add":
            track_ids = parse_ids(args.track_ids)
            session.playlist(args.playlist_id).add(track_ids)
            console.print(f"[green]Added {len(track_ids)} track(s)[/green]")

        case "playlist-remove":
            playlist = session.playlist(args.playlist_id)
            if args.track_ids:
                for tid in parse_ids(args.track_ids):
                    playlist.remove_by_id(tid)
            elif args.indices:
                for idx in sorted([int(i) for i in parse_ids(args.indices)], reverse=True):
                    playlist.remove_by_index(idx)
            console.print(f"[green]Removed tracks[/green]")

        case "playlist-update":
            session.playlist(args.playlist_id).edit(title=args.title or None, description=args.description or None)
            console.print(f"[green]Updated playlist[/green]")

        case "playlist-reorder":
            session.playlist(args.playlist_id).move(args.from_index, args.to_index)
            console.print(f"[green]Moved track {args.from_index} → {args.to_index}[/green]")

        case _:
            console.print(f"[red]Unknown command: {args.command}[/red]")


if __name__ == "__main__":
    main()
