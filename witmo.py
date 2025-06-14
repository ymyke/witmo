import os
import argparse
import sys
from loguru import logger
from openai import OpenAI
from image import Image
from history import History
from llm_client import LLMClient

# global variables TODO
client: OpenAI
llm_client: LLMClient
chat_context: list = []
SYSTEM_PROMPT: str


def analyze_image(image: Image, question):
    logger.info(f"Sending image to llm...")
    logger.info(f"Analysis request: {question}")

    system_message = SYSTEM_PROMPT
    messages = [{"role": "system", "content": system_message}]

    for msg in history.last(10):
        if isinstance(msg.get("content"), (str, list)):
            messages.append(msg)

    user_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": question},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image.to_base64()}"},
            },
        ],
    }
    messages.append(user_message)
    # Use LLMClient for OpenAI call
    analysis = llm_client.chat_completion(messages)
    print("\n✅ Analysis from AI Assistant:")
    print("=" * 50)
    print(analysis)
    print("=" * 50)

    history.append(user_message)
    history.append({"role": "assistant", "content": analysis})

    return analysis


def chat_with_ai(initial_image: Image, initial_prompt: str):
    """Start an interactive chat session with the AI assistant (text only)"""
    print("\n" + "=" * 60)
    print("💬 STARTING INTERACTIVE CHAT SESSION 💬".center(60))
    print("=" * 60)
    print("• Type 'exit', 'quit', or 'bye' to end the chat")
    print("• Type 'capture' to take a new screenshot")
    print("• Type your questions or messages normally")
    print("-" * 60)

    response = analyze_image(initial_image, initial_prompt)
    while True:
        user_input = input("\n💬 Your message: ")

        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            print("👋 Ending chat session.")
            break

        # Normal chat interaction - no image for this message
        print(f"💬 Sending message to AI assistant...")

        system_message = SYSTEM_PROMPT
        messages = [{"role": "system", "content": system_message}]

        for msg in history.last(10):
            if isinstance(msg.get("content"), str):
                messages.append(msg)

        user_message = {"role": "user", "content": user_input}
        messages.append(user_message)
        ai_response = llm_client.chat_completion(messages)
        history.append(user_message)
        history.append({"role": "assistant", "content": ai_response})

        print("\n✅ AI Assistant:")
        print("-" * 60)
        print(ai_response)
        print("-" * 60)


def save_chat_history():
    history.save()


def load_chat_history():
    history.load()


def main(args: argparse.Namespace) -> None:

    print("\n" + "=" * 60)
    print("🎮 WITMO - GAMING ASSISTANT 🎮".center(60))
    print("=" * 60)
    print(f"GAME: {args.game_name}".center(60))
    print("-" * 60)
    print("• Capture gameplay, get advice, and chat with your AI assistant")
    print("• Conversation history is maintained for context")
    print("-" * 60)

    global llm_client, client, SYSTEM_PROMPT, history
    game_name_safe = args.game_name.replace(" ", "_").lower()
    output_dir = os.path.join("history", game_name_safe)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created directory: {output_dir}")

    client = OpenAI(api_key="REMOVED_KEY")
    llm_client = LLMClient(api_key="REMOVED_KEY")
    # TODO remove this key

    SYSTEM_PROMPT = f"""\
You are an expert gaming assistant for {args.game_name}. 
Your job is to analyze gameplay images and provide helpful, concise advice.
Focus ONLY on what's happening in the game.
Be specific and actionable, clear and concise. 
Never just read what you see on the screen, assume that the user can read it themselves.
"""

    history = History(output_dir)

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
    save_chat_history()
    print("\n👋 Thanks for using Witmo!")


if __name__ == "__main__":
    # Do all the argument parsing here:
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

    args = parser.parse_args()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    main(args)
