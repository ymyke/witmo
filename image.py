import os
import datetime
import base64
import threading
import cv2
import os
from loguru import logger


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

    def preview(self, seconds=5, preview_width=400):
        """Open the image using OpenCV, show at full resolution but start with a small
        window (non-blocking, aspect ratio preserved).
        """

        def _show():
            try:
                logger.debug(f"Attempting to show image: {self.path}")
                img = cv2.imread(self.path)

                # Scale:
                h, w = img.shape[:2]
                if w > preview_width:
                    scale = preview_width / w
                    win_w = int(w * scale)
                    win_h = int(h * scale)
                else:
                    win_w, win_h = w, h

                logger.debug(
                    f"Image loaded. Displaying window at {win_w}x{win_h}, image is {w}x{h}."
                )

                # Show & wait:
                cv2.namedWindow("Witmo Capture", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Witmo Capture", win_w, win_h)
                cv2.imshow("Witmo Capture", img)
                try:
                    cv2.setWindowProperty("Witmo Capture", cv2.WND_PROP_TOPMOST, 1)
                except Exception as e:
                    logger.debug(f"Could not set window as topmost: {e}")
                cv2.waitKey(1)
                logger.debug(f"Image window should now be visible for {seconds} seconds.")
                cv2.waitKey(seconds * 1000)
                cv2.destroyAllWindows()
                logger.debug(f"Image window closed.")
            except Exception as e:
                logger.warning(f"Could not display image: {e}")

        threading.Thread(target=_show, daemon=True).start()

    @classmethod
    def create_with_timestamp(cls, output_dir: str, prefix: str = "cap") -> "Image":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"{prefix}_{timestamp}.jpg")
        return cls(filename)
