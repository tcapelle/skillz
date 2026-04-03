import requests
import urllib3

# Suppress self-signed cert warnings from WiiM/LinkPlay
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_HOST = "192.168.1.13"

SOURCE_NAMES = {
    "0": "Idle",
    "1": "AirPlay",
    "2": "DLNA",
    "10": "WiFi",
    "11": "USB",
    "31": "Spotify",
    "32": "Tidal",
    "40": "Line-In",
    "41": "Bluetooth",
    "43": "Optical",
    "99": "Multiroom Slave",
}

LOOP_MODES = {
    "0": "Loop All",
    "1": "Loop One",
    "2": "Shuffle + Loop",
    "3": "Shuffle",
    "4": "Sequential",
}


def api(host: str, command: str) -> str | dict:
    """Send a command to the WiiM HTTP API. Returns parsed JSON or raw text."""
    url = f"https://{host}/httpapi.asp?command={command}"
    resp = requests.get(url, verify=False, timeout=5)
    resp.raise_for_status()
    try:
        return resp.json()
    except requests.exceptions.JSONDecodeError:
        return resp.text


def hex_decode(s: str) -> str:
    """Decode hex-encoded strings from WiiM metadata."""
    try:
        return bytes.fromhex(s).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return s


def now_playing(host: str) -> dict:
    """Get current playback state with decoded metadata."""
    status = api(host, "getPlayerStatus")
    return {
        "status": status.get("status", "unknown"),
        "source": SOURCE_NAMES.get(str(status.get("mode", "")), f"Unknown ({status.get('mode')})"),
        "vendor": status.get("vendor", ""),
        "title": hex_decode(status.get("Title", "")),
        "artist": hex_decode(status.get("Artist", "")),
        "album": hex_decode(status.get("Album", "")),
        "position_s": int(status.get("curpos", 0)) // 1000,
        "duration_s": int(status.get("totlen", 0)) // 1000,
        "volume": int(status.get("vol", 0)),
        "muted": status.get("mute", "0") == "1",
        "loop": LOOP_MODES.get(str(status.get("loop", "")), "Unknown"),
    }
