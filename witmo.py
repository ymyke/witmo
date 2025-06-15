import sys
from loguru import logger
from image import Image
from argparsing import parse
from llm import generate_completion
from session import Session

main_greeting = """\
============================================================
                🎮 WITMO - GAMING ASSISTANT 🎮
============================================================
                      GAME: {game_name}
------------------------------------------------------------
• Capture gameplay, get advice, and chat with your AI assistant
• Conversation history is maintained for context
------------------------------------------------------------
"""

chat_greeting = """\
============================================================
                 💬 STARTING CHAT SESSION 💬
============================================================
• Ask your follow-up questions.
• 'q/quit': Back to main loop
• 'capture': Take a new screenshot
------------------------------------------------------------
"""

chat_response_pattern = """\
Response:
============================================================
{response}
============================================================
"""


# TODO rename functions?


def chat_with_ai(initial_image: Image, initial_prompt: str, session: Session) -> None:
    print(chat_greeting)

    print(f"Sent. Waiting for a response...")
    response = generate_completion(
        initial_prompt,
        image=initial_image,
        history=session.history,
        SYSTEM_PROMPT=session.system_prompt,
    )
    print(chat_response_pattern.format(response=response))
    while True:
        user_input = input("\n💬 Your message: ")

        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            print("Ending chat session.")
            break

        print(f"Sent. Waiting for a response...")
        response = generate_completion(
            user_input,
            history=session.history,
            SYSTEM_PROMPT=session.system_prompt,
        )
        print(chat_response_pattern.format(response=response))


def main() -> None:
    args = parse()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)

    session = Session.from_args(args)
    session.history.load()

    # Camera selection logic:
    if args.test_camera:
        logger.info("Using TestCamera for local testing. No ADB connection required.")
        from test_camera import TestCamera

        camera = TestCamera(args.delete_remote, session.output_dir)
    else:
        from adb_camera import AdbCamera

        camera = AdbCamera(args.delete_remote, session.output_dir)

    print(main_greeting.format(game_name=args.game_name))

    with camera:
        image = Image(args.initial_image) if args.initial_image else None
        while True:
            if not image:
                key = input(
                    "\nPress Enter to capture a new image or type 'q' to quit: "
                )
                # TODO switch to non-blocking input
                if key == "q":
                    break
                image = camera.capture()

            image.preview()

            # TODO do proper prompt selection here
            prompt = f"{args.game_name}: Describe what we see here and help me understand what's happening. Do not just read out what is there. I can read the screen myself. Focus on giving me insights, help me understand, provide truly useful information."
            chat_with_ai(image, prompt, session)

            image = None

    print("\n🔄 Saving chat history...")
    session.history.save()
    print("\n👋 Thanks for using Witmo!")


if __name__ == "__main__":
    main()
