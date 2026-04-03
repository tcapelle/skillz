import json
import socket
import time
from dataclasses import dataclass
from urllib.parse import quote

import requests
import simple_parsing as sp
import tidalapi
import urllib3
from rich.console import Console
from zeroconf import ServiceBrowser, Zeroconf

from tidal_bridge import (
    build_queue_xml,
    create_temp_playlist_and_play,
    get_tidal_session,
    push_queue_and_play,
)
from wiim_device import (
    api,
    hex_decode,
    now_playing,
    resolve_device,
    save_devices,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console()

COMMANDS = [
    "discover", "status", "device",
    "play", "pause", "toggle", "stop", "next", "prev",
    "volume", "mute", "unmute", "seek", "loop",
    "play-url", "play-tidal",
]


@dataclass
class Args:
    """Control WiiM audio devices"""
    command: str              # discover, status, device, play, pause, toggle, stop, next, prev, volume, mute, unmute, seek, loop, play-url, play-tidal
    value: str = ""           # Value for volume/seek/loop/URL, or search query for play-tidal
    device: str | None = None # Device name (partial match OK, auto-selects if only one)
    timeout: int = 5          # Discovery timeout in seconds
    type: str = "tracks"      # For play-tidal: tracks, album, artist, playlist
    playlist_id: str = ""     # For play-tidal: play a specific Tidal playlist by ID
    limit: int = 20           # For play-tidal: max tracks


def cmd_discover(timeout: int):
    class Listener:
        def __init__(self):
            self.services = []
        def add_service(self, zc, type_, name):
            info = zc.get_service_info(type_, name)
            if info:
                self.services.append(info)
        def remove_service(self, *a): pass
        def update_service(self, *a): pass

    console.print(f"Scanning ({timeout}s)...")
    zc = Zeroconf()
    listener = Listener()
    ServiceBrowser(zc, "_airplay._tcp.local.", listener)
    time.sleep(timeout)
    zc.close()

    devices = {}
    for svc in listener.services:
        for addr in svc.addresses:
            ip = socket.inet_ntoa(addr)
            try:
                data = api(ip, "getStatusEx")
                if isinstance(data, dict) and "DeviceName" in data:
                    name = data["DeviceName"]
                    devices[name] = {
                        "ip": ip, "name": name,
                        "model": data.get("priv_prj", ""),
                        "firmware": data.get("firmware", ""),
                    }
                    console.print(f"  [green]✓[/green] {name} ({ip})")
            except Exception:
                pass

    if devices:
        save_devices(devices)
        console.print(f"[green]{len(devices)} device(s) saved[/green]")
    else:
        console.print("[red]No WiiM devices found[/red]")
    console.print_json(json.dumps(devices, indent=2))


def cmd_play_tidal(host: str, args):
    session = get_tidal_session()

    if args.playlist_id:
        # Existing playlist — use its ID directly as SearchUrl
        playlist = session.playlist(args.playlist_id)
        tracks = list(playlist.items(limit=args.limit))
        name = playlist.name
        queue_xml = build_queue_xml(name, tracks, playlist_id=args.playlist_id)
        console.print(f"[green]Playing {len(tracks)} track(s): {name}[/green]")
        for i, t in enumerate(tracks[:5], 1):
            console.print(f"  {i}. {t.name} — {t.artist.name}")
        if len(tracks) > 5:
            console.print(f"  ... and {len(tracks) - 5} more")
        push_queue_and_play(host, name, queue_xml)
        return

    # Ad-hoc play: search → create temp playlist → push to WiiM → delete playlist
    if args.type == "artist":
        results = session.search(args.value, models=[tidalapi.Artist], limit=1)
        artists = results.get("artists", [])
        if not artists:
            console.print(f"[red]No artist found for '{args.value}'[/red]")
            return
        artist = artists[0]
        tracks = artist.get_top_tracks(limit=args.limit)
        name = f"{artist.name} — Top Tracks"

    elif args.type == "album":
        results = session.search(args.value, models=[tidalapi.Album], limit=1)
        albums = results.get("albums", [])
        if not albums:
            console.print(f"[red]No album found for '{args.value}'[/red]")
            return
        album = albums[0]
        tracks = album.tracks()
        name = f"{album.artist.name} — {album.name}"

    else:
        results = session.search(args.value, models=[tidalapi.Track], limit=args.limit)
        tracks = results.get("tracks", [])
        if not tracks:
            console.print(f"[red]No tracks found for '{args.value}'[/red]")
            return
        name = f"Search: {args.value}"

    console.print(f"[green]Playing {len(tracks)} track(s): {name}[/green]")
    for i, t in enumerate(tracks[:5], 1):
        console.print(f"  {i}. {t.name} — {t.artist.name}")
    if len(tracks) > 5:
        console.print(f"  ... and {len(tracks) - 5} more")

    create_temp_playlist_and_play(session, host, name, tracks)


def main():
    args = sp.parse(Args)

    if args.command == "discover":
        return cmd_discover(args.timeout)

    host = resolve_device(args.device)

    match args.command:
        case "play-tidal":
            cmd_play_tidal(host, args)
        case "status":
            console.print_json(json.dumps(now_playing(host)))
        case "device":
            info = api(host, "getStatusEx")
            console.print_json(json.dumps({
                "name": info.get("DeviceName"),
                "firmware": info.get("firmware"),
                "ip": info.get("apcli0"),
                "mac": info.get("MAC"),
                "wifi_ssid": hex_decode(info.get("essid", "")),
                "wifi_rssi": info.get("RSSI"),
            }))
        case "play":    api(host, "setPlayerCmd:resume"); console.print("[green]Playing[/green]")
        case "pause":   api(host, "setPlayerCmd:pause"); console.print("[yellow]Paused[/yellow]")
        case "stop":    api(host, "setPlayerCmd:stop"); console.print("[red]Stopped[/red]")
        case "toggle":  api(host, "setPlayerCmd:onepause"); console.print(f"[cyan]{now_playing(host)['status'].capitalize()}[/cyan]")
        case "next":    api(host, "setPlayerCmd:next"); console.print("[green]Next[/green]")
        case "prev":    api(host, "setPlayerCmd:prev"); console.print("[green]Previous[/green]")
        case "mute":    api(host, "setPlayerCmd:mute:1"); console.print("[yellow]Muted[/yellow]")
        case "unmute":  api(host, "setPlayerCmd:mute:0"); console.print("[green]Unmuted[/green]")
        case "volume":
            if args.value:
                api(host, f"setPlayerCmd:vol:{args.value}")
                console.print(f"[green]Volume: {args.value}[/green]")
            else:
                console.print(f"Volume: {now_playing(host)['volume']}")
        case "seek":
            api(host, f"setPlayerCmd:seek:{args.value}")
            console.print(f"[green]Seek: {args.value}s[/green]")
        case "loop":
            modes = {"all": "0", "one": "1", "shuffle_loop": "2", "shuffle": "3", "sequential": "4"}
            api(host, f"setPlayerCmd:loopmode:{modes.get(args.value, args.value)}")
            console.print(f"[green]Loop: {args.value}[/green]")
        case "play-url":
            api(host, f"setPlayerCmd:play:{quote(args.value, safe='')}")
            console.print("[green]Playing URL[/green]")
        case _:
            console.print(f"[red]Unknown: {args.command}[/red]")


if __name__ == "__main__":
    main()
