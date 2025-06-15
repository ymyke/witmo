import argparse
import sys

def parse():
    help_epilog = """\
example Usage:
python witmo.py "Baldur's Gate 3"
python witmo.py "Elden Ring" -d -i myowncapture.jpg

prerequisites:
Connect your Android device via USB with ADB debugging enabled. Have your
camera app open and top of screen on the device.
"""
    parser = argparse.ArgumentParser(
        prog="witmo.py",
        description="Witmo — your AI gaming assistant",
        epilog=help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "game_name",
        help="name of the game being played",
    )
    parser.add_argument(
        "-i",
        "--initial-image",
        dest="initial_image",
        help="path to an initial image to analyze instead of capturing one",
    )
    parser.add_argument(
        "-d",
        "--delete-remote",
        dest="delete_remote",
        action="store_true",
        default=False,
        help="delete the image on the camera device after capturing",
    )
    parser.add_argument(
        "-t",
        "--test-camera",
        dest="test_camera",
        action="store_true",
        default=False,
        help="use test camera",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        dest="log_level",
        default="ERROR",
        choices=["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"],
        help="set loguru log level (default: ERROR)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()
