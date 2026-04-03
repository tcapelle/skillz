import json
import socket
import time
from dataclasses import dataclass
from urllib.parse import quote

import requests
import simple_parsing as sp
import urllib3
from rich.console import Console
from zeroconf import ServiceBrowser, Zeroconf

from wiim_device import (
    api,
    hex_decode,
    now_playing,
    resolve_device,
    save_devices,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console()


@dataclass
class Args:
    """Control WiiM audio devices"""
    command: str              # discover, status, device, play, pause, toggle, stop, next, prev, volume, mute, unmute, seek, loop, play-url
    value: str = ""           # Value for volume (0-100), seek (seconds), loop mode, or URL
    device: str | None = None # Device name (partial match OK, auto-selects if only one)
    timeout: int = 5          # Discovery timeout in seconds


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


def main():
    args = sp.parse(Args)

    if args.command == "discover":
        return cmd_discover(args.timeout)

    host = resolve_device(args.device)

    match args.command:
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
