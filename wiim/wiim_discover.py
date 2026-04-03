import json
import socket
import time
from dataclasses import dataclass

import requests
import simple_parsing as sp
import urllib3
from rich.console import Console
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

from wiim_device import save_devices

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console()


@dataclass
class Args:
    """Discover WiiM devices on the local network"""
    timeout: int = 5  # Seconds to wait for mDNS responses


def is_wiim_device(ip: str) -> dict | None:
    """Try the WiiM HTTPS API. Returns device info if it's a WiiM/LinkPlay device."""
    try:
        resp = requests.get(
            f"https://{ip}/httpapi.asp?command=getStatusEx",
            verify=False, timeout=3,
        )
        data = resp.json()
        if "DeviceName" in data:
            return {
                "ip": ip,
                "name": data["DeviceName"],
                "model": data.get("priv_prj", ""),
                "firmware": data.get("firmware", ""),
                "uuid": data.get("uuid", ""),
                "mac": data.get("MAC", ""),
            }
    except (requests.RequestException, ValueError):
        pass
    return None


class AirPlayListener:
    def __init__(self):
        self.services: list[ServiceInfo] = []

    def add_service(self, zc: Zeroconf, type_: str, name: str):
        info = zc.get_service_info(type_, name)
        if info:
            self.services.append(info)

    def remove_service(self, zc: Zeroconf, type_: str, name: str):
        pass

    def update_service(self, zc: Zeroconf, type_: str, name: str):
        pass


args = sp.parse(Args)
console.print(f"Scanning for WiiM devices ({args.timeout}s)...")

zc = Zeroconf()
listener = AirPlayListener()
browser = ServiceBrowser(zc, "_airplay._tcp.local.", listener)
time.sleep(args.timeout)
zc.close()

console.print(f"Found {len(listener.services)} AirPlay services, checking for WiiM devices...")

devices = {}
for svc in listener.services:
    for addr in svc.addresses:
        ip = socket.inet_ntoa(addr)
        info = is_wiim_device(ip)
        if info:
            devices[info["name"]] = info
            console.print(f"  [green]✓[/green] {info['name']} ({ip}) — {info['model']}")

if devices:
    save_devices(devices)
    console.print(f"\n[green]{len(devices)} WiiM device(s) saved to ~/.wiim/devices.json[/green]")
else:
    console.print("[red]No WiiM devices found on the network[/red]")

console.print_json(json.dumps(devices, indent=2))
