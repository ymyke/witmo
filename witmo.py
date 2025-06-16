import sys
from loguru import logger
from image import Image
from argparsing import parse
from session import Session
from mainloop import mainloop
from print_utils import pw

main_greeting = """\
============================================================
                🎮 WITMO - G{{AI}}MING COACH 🎮
============================================================
                      GAME: {game_name}
------------------------------------------------------------
• Capture gameplay, get advice, and chat with your AI coach
• Conversation history is maintained for context
------------------------------------------------------------
"""


def start_witmo() -> None:
    args = parse()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)

    session = Session.from_args(args)
    session.history.load()

    pw(main_greeting.format(game_name=args.game_name))

    with session.camera:
        image = Image(args.initial_image) if args.initial_image else None
        mainloop(session, image)

    pw("\n🔄 Saving chat history...")
    session.history.save()
    pw("\n👋 Thanks for using Witmo!")


if __name__ == "__main__":
    start_witmo()
