import os
import random
from image import BasicImage
from loguru import logger
from .camera_protocol import CameraProtocol


class TestCamera(CameraProtocol):
    """A simple test camera that returns a random image from the output_dir on capture."""

    def __init__(self, do_delete_remote: bool = False, output_dir="captures"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            raise ValueError(f"Output directory does not exist: {self.output_dir}")

    def capture(self) -> BasicImage:
        images = [
            f
            for f in os.listdir(self.output_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
            and os.path.isfile(os.path.join(self.output_dir, f))
        ]
        if not images:
            logger.error(f"No images found in {self.output_dir}")
            raise RuntimeError(f"No images found in {self.output_dir}")
        chosen = random.choice(images)
        logger.info(f"Selected test image: {chosen}")
        return BasicImage(os.path.join(self.output_dir, chosen))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Return a random image from output_dir using TestCamera"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="captures",
        help="output directory for test images",
    )

    args = parser.parse_args()

    with TestCamera(args.output) as camera:
        image = camera.capture()
        logger.info(f"Test image selected: {image.path}")
