import json
from dataclasses import dataclass

import simple_parsing as sp
from rich.console import Console

from wiim_device import resolve_device, api, now_playing

console = Console()


@dataclass
class Args:
    """WiiM device status"""
    action: str = "now_playing"  # now_playing or device
    device: str | None = None    # Device name (partial match OK). Auto-selects if only one device.


args = sp.parse(Args)
host = resolve_device(args.device)

match args.action:
    case "now_playing":
        info = now_playing(host)
        console.print_json(json.dumps(info))

    case "device":
        info = api(host, "getStatusEx")
        summary = {
            "name": info.get("DeviceName"),
            "firmware": info.get("firmware"),
            "ip": info.get("apcli0"),
            "mac": info.get("MAC"),
            "wifi_ssid": bytes.fromhex(info.get("essid", "")).decode("utf-8", errors="replace"),
            "wifi_rssi": info.get("RSSI"),
            "uuid": info.get("uuid"),
        }
        console.print_json(json.dumps(summary))

    case _:
        console.print(f"[red]Unknown action: {args.action}. Use: now_playing, device[/red]")
