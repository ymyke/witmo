import os
import json
import argparse
import sys
from openai import OpenAI
import adb_camera
from image import Image

# global variables TODO
history_file: str
client: OpenAI
chat_context: list = []
SYSTEM_PROMPT: str



def analyze_image(image: Image, question):
    """Send an image to OpenAI's API for analysis"""
    print(f"Sending image to llm...")
    print(f"Analysis request: {question}")

    try:
        # Create a detailed prompt for gaming assistant
        system_message = SYSTEM_PROMPT
        messages = [{"role": "system", "content": system_message}]

        # Add chat history for context (limited to last 10 messages)
        for msg in chat_context[-10:]:
            # If the message is a vision/image message, keep as is

            # TODO so this works with both text and image messages?
            if isinstance(msg.get("content"), list):
                messages.append(msg)
            else:
                # Otherwise, ensure content is a string
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the current question with image
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image.to_base64()}"},
                    },
                ],
            }
        )
        # Send request to OpenAI's API
        # Convert message format to what OpenAI expects
        response = client.chat.completions.create(
            model="o3",
            messages=messages,
            # max_tokens=1000,
        )

        # Extract the analysis
        analysis = response.choices[0].message.content
        print("\n✅ Analysis from AI Assistant:")
        print("=" * 50)
        print(analysis)
        print("=" * 50)

        # Update chat context
        chat_context.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        )

        chat_context.append({"role": "assistant", "content": analysis})

        return analysis

    except Exception as e:
        print(f"❌ Error communicating with OpenAI API: {str(e)}")
        return f"Error analyzing image: {str(e)}"


def chat_with_ai(initial_image: Image, initial_prompt: str):
    """Start an interactive chat session with the AI assistant (text only)"""
    global chat_context

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

        # TODO necessary?
        # # Check for capture command
        # if user_input.lower() == "capture":
        #     print("🔄 Capturing new gameplay image...")
        #     new_image_path = capture_image()

        #     if new_image_path:
        #         follow_up = input(
        #             "\n❓ What would you like to know about this gameplay moment? "
        #         )
        #         if not follow_up.strip():
        #             follow_up = "Describe what we see here and help me understand what's happening."

        #         # Analyze the new image
        #         response = analyze_image(new_image_path, follow_up)
        #         continue
        #     else:
        #         print(
        #             "❌ Failed to capture new image. Continuing chat with previous context."
        #         )
        #         continue

        # Normal chat interaction - no image for this message
        print(f"💬 Sending message to AI assistant...")

        try:
            system_message = SYSTEM_PROMPT
            messages = [{"role": "system", "content": system_message}]

            # Add chat history (limited to last 10 messages)
            for msg in chat_context[-10:]:
                # Only add text messages (not vision/image messages)
                if isinstance(msg.get("content"), str):
                    messages.append({"role": msg["role"], "content": msg["content"]})

            # Add the current question
            user_message = {"role": "user", "content": user_input}
            messages.append(user_message)
            # Send request to OpenAI's API
            # Convert message format to what OpenAI expects
            response = client.chat.completions.create(
                model="o3",
                messages=messages,
                # max_tokens=1000,
            )

            # Extract the response
            ai_response = response.choices[0].message.content

            # Update chat context
            chat_context.append(user_message)
            chat_context.append({"role": "assistant", "content": ai_response})

            # Display the response
            print("\n✅ AI Assistant:")
            print("-" * 60)
            print(ai_response)
            print("-" * 60)

        except Exception as e:
            print(f"❌ Error in chat: {str(e)}")
            ai_response = "Sorry, I encountered a problem processing your request. Can you try again?"
            print(ai_response)


def save_chat_history():
    """Save the chat history to a file"""
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(chat_context, f, indent=2, ensure_ascii=False)
        print(f"✅ Chat history saved to {history_file}")
    except Exception as e:
        print(f"❌ Error saving chat history: {str(e)}")


def load_chat_history():
    """Load existing chat history if available"""
    global chat_context
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            # Only keep valid message dicts
            chat_context = []
            for msg in loaded:
                if (
                    isinstance(msg, dict)
                    and "role" in msg
                    and "content" in msg
                    and (
                        isinstance(msg["content"], str)
                        or isinstance(msg["content"], list)
                    )
                ):
                    chat_context.append(msg)
            print(f"✅ Loaded existing chat history with {len(chat_context)} messages")
        except json.JSONDecodeError:
            print("⚠️ Chat history file was corrupted, starting with empty history")
            chat_context = []
    else:
        print("ℹ️ No previous chat history found, starting fresh")
        chat_context = []


def main(args: argparse.Namespace) -> None:

    print("\n" + "=" * 60)
    print("🎮 WITMO - GAMING ASSISTANT 🎮".center(60))
    print("=" * 60)
    print(f"GAME: {args.game_name}".center(60))
    print("-" * 60)
    print("• Capture gameplay, get advice, and chat with your AI assistant")
    print("• Conversation history is maintained for context")
    print("-" * 60)

    global client, history_file, SYSTEM_PROMPT
    game_name_safe = args.game_name.replace(" ", "_").lower()
    output_dir = os.path.join("history", game_name_safe)
    history_file = os.path.join(output_dir, "chat_history.json")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    client = OpenAI(api_key="REMOVED_KEY")
    # TODO remove this key

    SYSTEM_PROMPT = f"""\
You are an expert gaming assistant for {args.game_name}. 
Your job is to analyze gameplay images and provide helpful, concise advice.
Focus ONLY on what's happening in the game.
Be specific and actionable, clear and concise. 
Never just read what you see on the screen, assume that the user can read it themselves.
"""

    load_chat_history()

    camera = adb_camera.AdbCamera(args.delete_remote, output_dir)
    camera.keep_screen_on(True)
    camera.set_brightness(0)

    image = Image(args.i) or None
    while True:
        if not image:
            key = input("\nPress Enter to capture a new image or type 'q' to quit: ")
            # TODO switch to non-blocking input
            if key == "q":
                break
            image = camera.capture()

        # TODO do proper prompt selection here
        prompt = f"{args.game_name}: Describe what we see here and help me understand what's happening. Do not just read out what is there. I can read the screen myself. Focus on giving me insights, help me understand, provide truly useful information."
        chat_with_ai(image, prompt)

        image = None

    print("\n🔄 Saving chat history...")
    save_chat_history()  # TODO does this work?
    camera.keep_screen_on(False)
    camera.set_brightness(1)
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
        help="delete the image on the camera device after capturing",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    main(args)
