"""
Simple ADB camera module for Witmo

This module provides a straightforward implementation of camera capture
via ADB over USB, with no abstractions or inheritance.

To set up adb:
1. Enable USB debugging in developer options
2. Connect your Android device via USB (default mode)
"""

# TODO some of the prints here should be logging statements

import os
import time
import datetime
import base64
from ppadb.client import Client as AdbClient

class CameraError(Exception):
    pass


class AdbCamera:
    """A simple class for capturing images via ADB USB connection"""

    def __init__(self, do_delete_remote: bool = False, output_dir="captures"):
        """
        Initialize the AdbCamera

        Args:
            output_dir (str): Directory where captured images will be stored
        """
        self.do_delete_remote = do_delete_remote

        if not output_dir:
            raise ValueError("Output directory must be specified")
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created directory: {self.output_dir}")

        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.device = self._get_device()
        print(f"Connected to device: {self.device.serial}")

    def _get_device(self):
        """Get the connected ADB device

        Returns:
            Device: The connected ADB device or None if no device is found
        """
        try:
            devices = self.client.devices()
        except Exception as e:
            raise CameraError(f"Failed to connect to ADB: {str(e)}")

        if not devices:
            raise CameraError(
                "No ADB devices found. Make sure your device is connected and USB debugging is enabled."
            )

        device = devices[0]
        return device

    def set_brightness(self, level: int) -> None:
        """Set the device screen brightness

        Args:
            level (int): Brightness level (0-255)
        """
        if not (0 <= level <= 255):
            raise ValueError("Brightness level must be between 0 and 255")

        try:
            print(f"Setting screen brightness to {level}...")
            self.device.shell(f"settings put system screen_brightness {level}")
        except Exception as e:
            print(f"Error setting brightness: {str(e)}")

    def keep_screen_on(self, enable=True) -> None:
        """Keep the screen on while connected via USB

        Args:
            enable (bool): True to keep screen on, False to restore default
        """
        try:
            if enable:
                print("🔓 Keeping device screen on...")
                self.device.shell("svc power stayon usb")
            else:
                print("🔒 Restoring normal screen timeout...")
                self.device.shell("svc power stayon false")
        except Exception as e:
            print(f"Error changing screen timeout: {str(e)}")

    def get_latest_image_path(self) -> str:
        """Get the most recent image from the device's camera

        Returns:
            str: Path to the latest image file on device
        """
        output = self.device.shell(
            "ls -t /sdcard/DCIM/Camera | head -n1"
        ).strip()  # TODO path
        return f"/sdcard/DCIM/Camera/{output}"

    def assert_running(self) -> None:
        """Ensure the camera app is running on the device."""
        output = self.device.shell("top -n 1")
        if not any("camera" in line.lower() for line in output.splitlines()):
            raise CameraError(
                "Camera app is not running. Please open the camera app on your device."
            )


    def capture(self) -> str:
        """Capture an image using the device's camera

        Returns:
            str: Path to the captured image file
        """
        print("📸 Taking photo...")
        
        self.assert_running()

        latest_image_before = self.get_latest_image_path()
        self.device.shell("input keyevent KEYCODE_CAMERA")

        # Wait for the camera to save the image:
        i = 0
        while True:
            time.sleep(0.05)
            latest_image = self.get_latest_image_path()
            if latest_image != latest_image_before:
                break
            i += 1
            if i > 20/0.05:
                raise CameraError(
                    "Timed out waiting for camera to save image. Please ensure the camera app is functioning."
                )

        print(f"Found recent image at {latest_image}")
        print(f"Transferring image to local machine...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        local_filename = os.path.join(self.output_dir, f"cap_{timestamp}.jpg")
        self.device.pull(latest_image, local_filename)

        if self.do_delete_remote:
            print("Removing image from device...")
            self.device.shell(f"rm '{latest_image}'")

        print(f"Image saved to {local_filename}")
        return local_filename

    @staticmethod
    def encode_image(image_path: str) -> str:
        """Encode an image to base64 for API transmission

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Base64-encoded image data
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


# Convenience functions for direct use
def encode_image_to_base64(image_path: str) -> str:
    """Encode an image to base64 for API transmission"""
    return AdbCamera.encode_image(image_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Capture images from Android device via ADB"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="captures",
        help="output directory for captured images",
    )
    parser.add_argument(
        "--delete-remote",
        "-d",
        action="store_true",
        help="delete the remote image after capture",
    )

    args = parser.parse_args()

    camera = AdbCamera(args.delete_remote, args.output)
    camera.keep_screen_on(True)

    try:
        image_path = camera.capture()
        if image_path:
            print(f"Image captured successfully: {image_path}")
        else:
            print("Image capture failed")
            exit(1)
    finally:
        camera.keep_screen_on(False)
