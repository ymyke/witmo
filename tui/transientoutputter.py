import time
from rich.live import Live
from rich.console import Group
from rich.panel import Panel
from rich.console import Console


class TransientOutputter:
    """Displays transient messages in a live console output."""

    def __init__(self, muted_color: str = "dim"):
        self._messages = []
        self._live = Live(Group(), auto_refresh=False)
        self._muted_color = muted_color
        # Tracks its state so start and flush can be called multiple times:
        self._active = False

    def start(self):
        if not self._active:
            self._live.__enter__()
            self._active = True

    def flush(self):
        if self._active:
            self.clear()
            self._live.__exit__(None, None, None)
            self._active = False

    def add(self, msg):
        """Add a renderable to the transient output."""
        self.start()  # Ensure the live console is active
        self._messages.append(msg)
        self._update()

    def clear(self):
        """Remove all messages from the display."""
        self._messages.clear()
        self._update()

    def _visible_tail(self):
        """Get the most recent messages that fit in the console. Because live console
        cannot scroll beyond its size.
        """
        console = self._live.console
        max_lines = console.size.height
        tail = []
        used = 0
        # Walk messages from newest → oldest until we fill the screen:
        for msg in reversed(self._messages):
            # Get how many lines this renderable will occupy:
            lines = console.render_lines(msg, console.options, pad=False)
            count = len(lines)
            if used + count > max_lines:
                break
            tail.append(msg)
            used += count
        return list(reversed(tail))

    def _update(self):
        group = Group(*self._visible_tail())
        self._live.update(group, refresh=True)


# Example usage:
if __name__ == "__main__":

    console = Console()
    to = TransientOutputter()
    for i in range(1, 6):
        time.sleep(0.5)
        to.add(f"step {i}/5 complete")
    panel = Panel("Almost there!", style="yellow")
    to.add(panel)
    time.sleep(1.0)
    to.add("Will clear in 1 second…")
    time.sleep(1.0)
    to.flush()

    console.print("Non-transient message")
    console.print(Panel("Non-transient panel", style="green"))
    time.sleep(5)
    for i in range(1, 5):
        to.add("New transient message")
        time.sleep(0.5)
    to.flush()

    console.print("Another non-transient message")
    console.print(Panel("That's it, non-transient", style="red"))
