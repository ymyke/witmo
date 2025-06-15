import os
import argparse
import sys
from loguru import logger
from image import Image
from history import History
from argparsing import parse
from llm import generate_completion


# global variables TODO
SYSTEM_PROMPT: str

# TODO rename functions?


def chat_with_ai(initial_image: Image, initial_prompt: str):
    """Start an interactive chat session with the AI assistant (text only)"""
    print("\n" + "=" * 60)
    print("💬 STARTING INTERACTIVE CHAT SESSION 💬".center(60))
    print("=" * 60)
    print("• Type 'exit', 'quit', or 'bye' to end the chat")
    print("• Type 'capture' to take a new screenshot")
    print("• Type your questions or messages normally")
    print("-" * 60)

    answer_pattern = """\
Response:
============================================================
{response}
============================================================
"""

    print(f"Sent. Waiting for a response...")
    response = generate_completion(
        initial_prompt,
        image=initial_image,
        history=history,
        SYSTEM_PROMPT=SYSTEM_PROMPT,
    )
    print(answer_pattern.format(response=response))
    while True:
        user_input = input("\n💬 Your message: ")

        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            print("Ending chat session.")
            break

        print(f"Sent. Waiting for a response...")
        response = generate_completion(
            user_input,
            history=history,
            SYSTEM_PROMPT=SYSTEM_PROMPT,
        )
        print(answer_pattern.format(response=response))




def main(args: argparse.Namespace) -> None:

    print("\n" + "=" * 60)
    print("🎮 WITMO - GAMING ASSISTANT 🎮".center(60))
    print("=" * 60)
    print(f"GAME: {args.game_name}".center(60))
    print("-" * 60)
    print("• Capture gameplay, get advice, and chat with your AI assistant")
    print("• Conversation history is maintained for context")
    print("-" * 60)

    global SYSTEM_PROMPT, history   # TODO
    game_name_safe = args.game_name.replace(" ", "_").lower()
    output_dir = os.path.join("history", game_name_safe)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created directory: {output_dir}")


    SYSTEM_PROMPT = f"""\
You are an expert gaming assistant for {args.game_name}. 
Your job is to analyze gameplay images and provide helpful, concise advice.
Focus ONLY on what's happening in the game.
Be specific and actionable, clear and concise. 
Never just read what you see on the screen, assume that the user can read it themselves.
"""

    history = History(output_dir)
    history.load()

    # Camera selection logic:
    if args.test_camera:
        logger.info("Using TestCamera for local testing. No ADB connection required.")
        from test_camera import TestCamera

        camera_class = TestCamera
    else:
        from adb_camera import AdbCamera

        camera_class = AdbCamera

    with camera_class(args.delete_remote, output_dir) as camera:
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
            chat_with_ai(image, prompt)

            image = None

    print("\n🔄 Saving chat history...")
    history.save()
    print("\n👋 Thanks for using Witmo!")


if __name__ == "__main__":
    args = parse()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    main(args)
