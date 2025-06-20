import sys
from loguru import logger
from wakepy import keep
from argparsing import parse
from session import Session
from mainloop import mainloop
from image import BasicImage
from tui.io import tt, tp, welcome_panel

greeting_pattern = """\
🎮🎓 WITMO - G{{AI}}MING COACH 🎓🎮

• Capture gameplay situations and get advice
• Conversation history is maintained for context
• Spoiler-free by default, but that can be configured
• Run `witmo --help` for more info or check out the README


You're playing:

🤜 {game_name} 🤛

Enjoy!"""


def start_witmo() -> None:
    args = parse()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    logger.debug("Starting Witmo...")

    greeting = greeting_pattern.format(game_name=args.game_name.upper())
    tp(welcome_panel(greeting))

    session = Session.from_args(args)

    tt(
        "Deactivating sleep mode and screen lock on PC and phone, also dimming phone screen..."
    )
    with session.history, session.camera, keep.presenting():
        image = BasicImage(args.initial_image) if args.initial_image else None
        mainloop(session, image)
        tt(
            "Restoring sleep mode and screen lock on PC and phone, "
            "also restoring phone screen brightness..."
        )

    tp(welcome_panel("👋 Thanks for using Witmo!"))


if __name__ == "__main__":
    start_witmo()
