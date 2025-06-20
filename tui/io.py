"""Terminal user interface (TUI) output and input."""

import re
import time
from typing import Literal
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich import box
from .transientoutputter import TransientOutputter
from .textinput import TextInputApp

# Colors:
BG = "#1e1e2e"
TEXT = "white"
WELCOME_ACCENT = "#FF66CC"  # Neon Pink
REQUEST_ACCENT = "#3366FF"  # Sapphire Blue
RESPONSE_ACCENT = "#33FF99"  # Mint Green
MUTED = "#707070"
PRIO2COLOR = {
    "top": "#D4AF37",  # Muted Gold
    "med": "#8B5E3C",  # Chestnut Brown
    "low": "#78909C",  # Slate
}
ERROR_ACCENT = "#E06C75"  # Coral Red'ish


# Globals:
_console = Console()
_to = TransientOutputter(muted_color=MUTED)


def tt(thing=None, style: Literal["error"] | None = None) -> None:
    """Transient tui output."""
    thing = thing or ""
    if isinstance(thing, str):
        if style == "error":
            thing = Text(str(thing), style=ERROR_ACCENT, justify="center")
        else:
            thing = Text(str(thing), style=MUTED, justify="center")
    _to.add(thing)


def tp(thing):
    """Permanent tui output."""
    _to.flush()  # Clear transient output
    _console.print(thing)
    _console.print("\n")


def get_textinput(title: str) -> str:
    app = TextInputApp(label=title)
    return app.run() or ""


def welcome_panel(txt: str) -> Panel:
    return Panel(
        Text(txt, style=TEXT, justify="center"),
        box=box.HEAVY,
        style=f"{WELCOME_ACCENT} on {BG}",
        title_align="center",
        padding=(1, 4),
        expand=True,
    )


def request_panel(txt: str) -> Align:
    return Align(
        Panel(
            txt,
            box=box.ROUNDED,
            style=f"on {BG}",
            border_style=REQUEST_ACCENT,
            title=f"[{REQUEST_ACCENT}]Request 💭[/]",
            title_align="right",
            padding=(1, 2),
            expand=False,
            width=90,
        ),
        align="right",
    )


def response_panel(txt: str) -> Align:
    # Convert '•' bullets to Markdown format:
    txt = re.sub(r"^(\s*)•", r"\1- ", txt, flags=re.MULTILINE)

    return Align(
        Panel(
            Markdown(txt, style=TEXT),
            box=box.ROUNDED,
            style=f"on {BG}",
            border_style=RESPONSE_ACCENT,
            title=f"[{RESPONSE_ACCENT}]💬 Response[/]",
            title_align="left",
            padding=(1, 2),
            expand=False,
            width=90,
        ),
        align="left",
    )


def menu_panel(title: str, items: list, prio: Literal["top", "med", "low"]) -> Align:
    color = PRIO2COLOR[prio]
    num_cols = len(items[0])
    table = Table(box=box.MINIMAL, expand=False, padding=(0, 1), show_header=False)
    for _ in range(num_cols):
        table.add_column()
    for row in items:
        table.add_row(*[str(cell) for cell in row])

    return Align(
        Panel(
            table,
            style=f"on {BG}",
            border_style=color,
            title=f"[bold {color}]{title}[/]",
            box=box.SQUARE,
            padding=(0, 10),
            expand=False,
        ),
        align="center",
    )


def dot_animation(stop_event, interval=0.4):
    seq = ["•", "••", "•••", "••••", "•••••"]
    i = 0
    while not stop_event.is_set():
        _to.clear()
        _to.add(Text(seq[i % len(seq)], style=MUTED, justify="left"))
        i += 1
        time.sleep(interval)
    _to.clear()
