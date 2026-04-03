import json
from dataclasses import dataclass
from urllib.parse import quote

import simple_parsing as sp
from rich.console import Console

from wiim_device import DEFAULT_HOST, api, now_playing

console = Console()


@dataclass
class Args:
    """WiiM playback control"""
    action: str               # play, pause, toggle, stop, next, prev, volume, mute, unmute, seek, loop, play_url
    host: str = DEFAULT_HOST  # WiiM device hostname or IP
    value: str = ""           # Volume (0-100), seek position (seconds), loop mode, or URL to play


args = sp.parse(Args)

match args.action:
    case "play":
        api(args.host, "setPlayerCmd:resume")
        console.print("[green]Playing[/green]")

    case "pause":
        api(args.host, "setPlayerCmd:pause")
        console.print("[yellow]Paused[/yellow]")

    case "toggle":
        api(args.host, "setPlayerCmd:onepause")
        info = now_playing(args.host)
        console.print(f"[cyan]{info['status'].capitalize()}[/cyan]")

    case "stop":
        api(args.host, "setPlayerCmd:stop")
        console.print("[red]Stopped[/red]")

    case "next":
        api(args.host, "setPlayerCmd:next")
        console.print("[green]Next track[/green]")

    case "prev":
        api(args.host, "setPlayerCmd:prev")
        console.print("[green]Previous track[/green]")

    case "volume":
        if args.value:
            api(args.host, f"setPlayerCmd:vol:{args.value}")
            console.print(f"[green]Volume set to {args.value}[/green]")
        else:
            info = now_playing(args.host)
            console.print(f"Volume: {info['volume']}")

    case "mute":
        api(args.host, "setPlayerCmd:mute:1")
        console.print("[yellow]Muted[/yellow]")

    case "unmute":
        api(args.host, "setPlayerCmd:mute:0")
        console.print("[green]Unmuted[/green]")

    case "seek":
        api(args.host, f"setPlayerCmd:seek:{args.value}")
        console.print(f"[green]Seeked to {args.value}s[/green]")

    case "loop":
        modes = {"all": "0", "one": "1", "shuffle_loop": "2", "shuffle": "3", "sequential": "4"}
        mode = modes.get(args.value, args.value)
        api(args.host, f"setPlayerCmd:loopmode:{mode}")
        console.print(f"[green]Loop mode: {args.value}[/green]")

    case "play_url":
        encoded_url = quote(args.value, safe="")
        api(args.host, f"setPlayerCmd:play:{encoded_url}")
        console.print(f"[green]Playing URL[/green]")

    case _:
        console.print(f"[red]Unknown action: {args.action}. Use: play, pause, toggle, stop, next, prev, volume, mute, unmute, seek, loop, play_url[/red]")
