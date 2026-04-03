import webbrowser
from pathlib import Path

import tidalapi

SESSION_FILE = Path.home() / ".tidal" / "session.json"


def fetch_all_items(fetch_func, max_items: int | None = None, page_size: int = 100) -> list:
    """Generic pagination helper for Tidal API endpoints that use limit/offset."""
    all_items = []
    offset = 0
    while True:
        batch_size = page_size
        if max_items is not None:
            remaining = max_items - len(all_items)
            if remaining <= 0:
                break
            batch_size = min(page_size, remaining)

        try:
            items = fetch_func(limit=batch_size, offset=offset)
        except TypeError:
            # Some endpoints don't support offset
            items = fetch_func(limit=batch_size) if offset == 0 else []

        if not items:
            break
        all_items.extend(items)
        if len(items) < batch_size:
            break
        offset += len(items)
    return all_items


def load_session() -> tidalapi.Session | None:
    """Try to load an existing valid session. Returns None if invalid/missing."""
    if not SESSION_FILE.exists():
        return None
    session = tidalapi.Session()
    session.load_session_from_file(SESSION_FILE)
    if session.check_login():
        return session
    return None


def login() -> tidalapi.Session:
    """Login to Tidal via browser OAuth. Returns authenticated session."""
    SESSION_FILE.parent.mkdir(exist_ok=True)
    session = tidalapi.Session()
    login_obj, future = session.login_oauth()
    auth_url = login_obj.verification_uri_complete
    if not auth_url.startswith("http"):
        auth_url = "https://" + auth_url
    webbrowser.open(auth_url)
    print(f"Enter code: {login_obj.user_code}", flush=True)
    print(f"URL: {auth_url}", flush=True)
    print(f"Expires in {login_obj.expires_in}s", flush=True)
    future.result()
    session.save_session_to_file(SESSION_FILE)
    return session


def get_session() -> tidalapi.Session:
    """Load existing session or login via browser. Always returns authenticated session."""
    return load_session() or login()


# --- Formatters (shared across scripts) ---

def format_track(t) -> dict:
    return {
        "id": t.id,
        "title": t.name,
        "artist": t.artist.name,
        "album": t.album.name,
        "duration": t.duration,
        "url": f"https://tidal.com/browse/track/{t.id}",
    }


def format_album(a) -> dict:
    return {
        "id": a.id,
        "title": a.name,
        "artist": a.artist.name if a.artist else "Unknown",
        "release_date": str(a.release_date) if a.release_date else None,
        "num_tracks": a.num_tracks,
        "url": f"https://tidal.com/browse/album/{a.id}",
    }


def format_artist(a) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "url": f"https://tidal.com/browse/artist/{a.id}",
    }


def format_playlist(p) -> dict:
    return {
        "id": p.id,
        "title": p.name,
        "num_tracks": p.num_tracks,
        "url": f"https://tidal.com/browse/playlist/{p.id}",
    }
