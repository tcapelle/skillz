from dataclasses import dataclass

import simple_parsing as sp
from rich.console import Console
from rich.panel import Panel

from tidal_session import load_session, login, SESSION_FILE

console = Console()


@dataclass
class Args:
    """Tidal authentication"""
    status: bool = False  # Check session status without triggering login


args = sp.parse(Args)

if args.status:
    session = load_session()
    if session:
        console.print(Panel(
            f"User ID: {session.user.id}",
            title="Tidal Session Active",
            style="green",
        ))
    else:
        console.print("[red]No valid Tidal session. Run without --status to login.[/red]")
else:
    session = login()
    console.print(f"[green]Logged in. User ID: {session.user.id}[/green]")
