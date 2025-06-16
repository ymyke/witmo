class NoCamera:
    """A dummy camera class that does nothing."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def capture(self):
        raise RuntimeError(
            "No camera available. Please provide an initial image with -i or use text prompts only."
        )
