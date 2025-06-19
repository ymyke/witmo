import sys
from loguru import logger
from wakepy import keep
from argparsing import parse
from session import Session
from mainloop import mainloop
from tui.print_wrapped import pw
from image import BasicImage

main_greeting = """\
============================================================
                🎮 WITMO - G{{AI}}MING COACH 🎮
============================================================
                      GAME: {game_name}
------------------------------------------------------------
• Capture gameplay situations and get advice
• Conversation history is maintained for context
• Spoiler-free by default, but can be configured
------------------------------------------------------------
"""


def start_witmo() -> None:
    logger.debug("Starting Witmo...")
    args = parse()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)

    session = Session.from_args(args)

    pw(main_greeting.format(game_name=args.game_name))

    logger.info("Deactivating sleep mode and screen lock until end of session...")
    with session.history, session.camera, keep.presenting():
        image = BasicImage(args.initial_image) if args.initial_image else None
        mainloop(session, image)

    pw("\n👋 Thanks for using Witmo!")


if __name__ == "__main__":
    start_witmo()
