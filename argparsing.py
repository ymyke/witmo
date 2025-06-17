import argparse
import sys

def parse():
    help_epilog = """\
example usage:
  python witmo.py -g "Baldur's Gate 3"
  python witmo.py -g "Elden Ring" -c -d -s all=high story=none
  python witmo.py -g "Elden Ring" -i myowncapture.jpg

spoiler control:
  Use --spoilers to set what the llm should reveal. Format: CATEGORY=LEVEL.
  Categories: items, locations, enemies, bosses, story, lore, mechanics.
  Levels: none (no spoilers), low, medium, high.
  Example: --spoilers all=medium story=none lore=high mechanics=high
  'all' sets all categories; individual categories override.

prerequisites:
  Connect your Android device via USB with ADB debugging enabled. Have your
  camera app open and top of screen on the device.
"""
    parser = argparse.ArgumentParser(
        prog="witmo.py",
        description="Witmo — g{ai}ming coach",
        epilog=help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Regular options:
    parser.add_argument(
        "-g",
        "--game",
        dest="game_name",
        required=True,
        help="name of the game being played",
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
        "-s",
        "--spoilers",
        nargs="*",
        metavar="CATEGORY=LEVEL",
        default=["all=none"],
        help="set spoiler levels per category, e.g. --spoilers all=low story=none (default: all=none)",
    )
    parser.add_argument(
        "-c",
        "--crop",
        dest="crop",
        action="store_true",
        default=False,
        help="crop images to detected TV/screen before sending to LLM",
    )

    # Dev/debugging options:
    debug_group = parser.add_argument_group('dev/debugging options')
    debug_group.add_argument(
        "-i",
        "--initial-image",
        dest="initial_image",
        help="path to an initial image to analyze instead of capturing one",
    )
    debug_group.add_argument(
        "-tc",
        "--test-camera",
        dest="test_camera",
        action="store_true",
        default=False,
        help="use test camera; picks a random image from the history directory",
    )
    debug_group.add_argument(
        "-nc",
        "--no-camera",
        dest="no_camera",
        action="store_true",
        default=False,
        help="run without camera; only use initial image (-i) or text prompts",
    )
    debug_group.add_argument(
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
