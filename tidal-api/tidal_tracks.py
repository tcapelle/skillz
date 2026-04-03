import json
import concurrent.futures
from dataclasses import dataclass

import simple_parsing as sp
from rich.console import Console
from tidalapi.user import ItemOrder, OrderDirection

from tidal_session import get_session, fetch_all_items, format_track

console = Console()


@dataclass
class Args:
    """Tidal tracks: favorites and recommendations"""
    action: str = "favorites"   # favorites or recommend
    track_ids: str = ""         # Comma-separated seed track IDs (for recommend; uses favorites if empty)
    limit: int = 20             # Max favorites to fetch, or recommendations per seed track
    limit_seeds: int = 20       # Max favorite tracks to use as seeds when no track_ids given


def parse_ids(s: str) -> list[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


args = sp.parse(Args)
session = get_session()

match args.action:
    case "favorites":
        favorites = session.user.favorites

        def fetch_page(limit, offset):
            try:
                return list(favorites.tracks(limit=limit, offset=offset, order=ItemOrder.Date, order_direction=OrderDirection.Descending))
            except TypeError:
                return list(favorites.tracks(limit=limit, order=ItemOrder.Date, order_direction=OrderDirection.Descending)) if offset == 0 else []

        tracks = fetch_all_items(fetch_page, max_items=args.limit)
        output = [format_track(t) for t in tracks]
        console.print_json(json.dumps(output, default=str))

    case "recommend":
        seed_ids = parse_ids(args.track_ids)

        # If no seed IDs, use favorites
        if not seed_ids:
            favorites = session.user.favorites
            def fetch_page(limit, offset):
                try:
                    return list(favorites.tracks(limit=limit, offset=offset, order=ItemOrder.Date, order_direction=OrderDirection.Descending))
                except TypeError:
                    return list(favorites.tracks(limit=limit, order=ItemOrder.Date, order_direction=OrderDirection.Descending)) if offset == 0 else []

            fav_tracks = fetch_all_items(fetch_page, max_items=args.limit_seeds)
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

        output = {"seed_count": len(seed_ids), "recommendations": all_recs}
        console.print_json(json.dumps(output, default=str))

    case _:
        console.print(f"[red]Unknown action: {args.action}. Use: favorites, recommend[/red]")
