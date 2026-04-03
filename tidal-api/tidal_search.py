import json
from dataclasses import dataclass

import simple_parsing as sp
import tidalapi
from rich.console import Console

from tidal_session import get_session, format_track, format_album, format_artist, format_playlist

console = Console()

MODEL_MAP = {
    "tracks": [tidalapi.Track],
    "albums": [tidalapi.Album],
    "artists": [tidalapi.Artist],
    "playlists": [tidalapi.Playlist],
}


@dataclass
class Args:
    """Search Tidal catalog"""
    query: str            # Search query
    type: str = "all"     # Search type: all, tracks, albums, artists, playlists
    limit: int = 20       # Max results per type


args = sp.parse(Args)
session = get_session()

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
