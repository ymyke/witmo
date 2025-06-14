import os
import datetime
import base64


class Image:
    """Value object representing a captured image file."""

    def __init__(self, path: str):
        self.path = path

    def __str__(self):
        return self.path

    def to_base64(self) -> str:
        """Return base64-encoded contents of this image."""
        with open(self.path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @classmethod
    def create_with_timestamp(cls, output_dir: str, prefix: str = "cap") -> "Image":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"{prefix}_{timestamp}.jpg")
        return cls(filename)
