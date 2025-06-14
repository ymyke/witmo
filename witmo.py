import os
import json
import argparse
import sys
from openai import OpenAI
import adb_camera

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Witmo - Game Assistant without Voice")
parser.add_argument(
    "game_name",
    nargs="?",
    default="Unspecified Game",
    help="Name of the game being played",
)
parser.add_argument(
    "-i", help="Path to an initial image to analyze instead of capturing one"
)
parser.add_argument(
    "-d",
    action="store_true",
    dest="delete_remote",
    default=False,
    help="Delete the remote image after capturing",
)
args = parser.parse_args()

# --- CONFIG ---
# Create game-specific output directory
game_name_safe = args.game_name.replace(" ", "_").lower()
output_dir = os.path.join("history", game_name_safe)
history_file = os.path.join(output_dir, "chat_history.json")

# Initialize the OpenAI client
client = OpenAI(api_key="REMOVED_KEY")
# FIXME remove key

# Chat context to maintain conversation history
chat_context = []

# Create an ADB camera instance
camera = adb_camera.AdbCamera(args.delete_remote, output_dir)

SYSTEM_PROMPT = f"""You are an expert gaming assistant for {args.game_name}. 
Your job is to analyze gameplay images and provide helpful, concise advice.
Focus ONLY on what's happening in the game.
Be specific and actionable, clear and concise. 
Never just read what you see on the screen, assume that the user can read it themselves.
"""


def ensure_dirs():
    """Ensure required directories exist"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    # Also update the camera's output directory
    camera.set_output_dir(output_dir)


def analyze_image(image_path, question):
    """Send an image to OpenAI's API for analysis"""
    print(f"Sending image to llm...")
    print(f"Analysis request: {question}")

    try:
        # Create a detailed prompt for gaming assistant
        system_message = SYSTEM_PROMPT
        base64_image = adb_camera.encode_image_to_base64(image_path)
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
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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


def chat_with_ai(initial_image_path, initial_prompt: str):
    """Start an interactive chat session with the AI assistant (text only)"""
    global chat_context

    print("\n" + "=" * 60)
    print("💬 STARTING INTERACTIVE CHAT SESSION 💬".center(60))
    print("=" * 60)
    print("• Type 'exit', 'quit', or 'bye' to end the chat")
    print("• Type 'capture' to take a new screenshot")
    print("• Type your questions or messages normally")
    print("-" * 60)

    response = analyze_image(initial_image_path, initial_prompt)
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


def main():
    """Main program flow"""
    print("\n" + "=" * 60)
    print("🎮 WITMO - GAMING ASSISTANT 🎮".center(60))
    print("=" * 60)
    print(f"GAME: {args.game_name}".center(60))
    print("-" * 60)
    print("• Capture gameplay, get advice, and chat with your AI assistant")
    print("• Conversation history is maintained for context")
    print("-" * 60)

    ensure_dirs()
    load_chat_history()

    # Keep the device screen on during the session
    camera.keep_screen_on(True)
    camera.set_brightness(0)

    image = args.i or ""
    while True:
        if not image:
            # wait for nonblocking input:
            key = input("\nPress Enter to capture a new image or type 'q' to quit: ")
            # TODO switch to non-blocking input
            if key == "q":
                break
            image = camera.capture()

        # TODO do proper prompt selection here
        prompt = f"{args.game_name}: Describe what we see here and help me understand what's happening. Do not just read out what is there. I can read the screen myself. Focus on giving me insights, help me understand, provide truly useful information."
        chat_with_ai(image, prompt)

        image = ""

    print("\n🔄 Saving chat history...")
    save_chat_history()  # TODO does this work?
    camera.keep_screen_on(False)
    camera.set_brightness(1)
    print("\n👋 Thanks for using Witmo!")


def display_example_usage():
    """Display example usage information"""
    print("\nExample Usage:")
    print("-------------")
    print('python witmo.py "Elden Ring"')
    print("python witmo.py Minecraft")
    print('python witmo.py "Call of Duty: Warzone"')
    print('python witmo.py "Elden Ring" -i captures/elden_ring/cap_20250612_215322.jpg')
    print("\nConnect your Android device via USB with ADB debugging enabled")
    print("Use -i to analyze an existing image instead of capturing one")


if __name__ == "__main__":
    if len(sys.argv) == 1 or args.game_name == "Unspecified Game":
        print("\n⚠️ No game name provided. Please specify the game name.")
        display_example_usage()
        sys.exit(1)

    main()
