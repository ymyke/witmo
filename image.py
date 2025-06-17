"""
Image abstractions for Witmo.

Defines the LLM-compatible Image protocol, BasicImage (file-backed), and CroppedImage
(auto-crops to TV/screen using YOLOv8).

Provides preview and base64 encoding utilities for image handling and LLM input.
"""

from typing import Protocol
from loguru import logger
import os
import datetime
import numpy as np
import base64
import threading
import cv2
from ultralytics import YOLO

# FIXME The way BasicImage and CroppedImage is architected is a bit of a mess?

def preview_image_array(
    img: np.ndarray, seconds=5, preview_width=400, window_name="Witmo Capture"
):
    """Show a NumPy image array in a resizable OpenCV window (non-blocking)."""

    def _show():
        try:
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

            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, win_w, win_h)
            cv2.imshow(window_name, img)
            try:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
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


class Image(Protocol):
    """Protocol for LLM-compatible images."""

    def to_base64(self) -> str:
        ...

    def preview(self, seconds: int = 5, preview_width: int = 400) -> None:
        ...


class BasicImage:
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
        """Preview the image file using OpenCV."""
        img = cv2.imread(self.path)
        preview_image_array(img, seconds=seconds, preview_width=preview_width, window_name="Witmo Capture")

    @classmethod
    def create_with_timestamp(cls, output_dir: str, prefix: str = "cap") -> "BasicImage":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"{prefix}_{timestamp}.jpg")
        return cls(filename)


class CroppedImage:
    """Represents a cropped version of a BasicImage, held in memory. Initiator will crop
    to tv /screen region automatically.
    """ 
    _yolo_model = YOLO("yolov8n.pt")
    _tv_class_id = 62  # COCO class ID for 'tvmonitor'

    def __init__(self, source_image: BasicImage):
        self.source_image = source_image
        img = cv2.imread(source_image.path)
        self.crop_rect = self._find_tv_screen(img)
        x, y, w, h = self.crop_rect
        self._cropped_array = img[y:y+h, x:x+w]

    def _find_tv_screen(self, img):
        """Use YOLOv8 to detect the TV/screen region. Returns (x, y, w, h) of the first
        detected TV, or full image if not found.
        """
        logger.debug("Finding screen...")
        results = self._yolo_model(img)
        for r in results:
            for b in r.boxes:
                if int(b.cls[0]) == self._tv_class_id:
                    x1, y1, x2, y2 = b.xyxy[0].cpu().numpy().astype(int)
                    logger.debug(f"Found TV at {x1}, {y1}, {x2}, {y2}")
                    return (x1, y1, x2 - x1, y2 - y1)
        # Fallback: full image:
        h, w = img.shape[:2]
        logger.debug("No TV found, using full image.")
        return (0, 0, w, h)

    def preview(self, seconds=5, preview_width=400):
        preview_image_array(self._cropped_array, seconds=seconds, preview_width=preview_width, window_name="Witmo Cropped Capture")

    def to_base64(self) -> str:
        _, buf = cv2.imencode('.jpg', self._cropped_array)
        return base64.b64encode(buf.tobytes()).decode("utf-8")
