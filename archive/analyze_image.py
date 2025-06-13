import os
import base64
from openai import OpenAI
import sys


def encode_image(image_path):
    """Encode an image to base64 for API transmission"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def speak_text(text, voice="echo"):
    """Convert text to speech using OpenAI's TTS API and play it"""
    print(f"🔊 Converting text to speech using voice: {voice}...")

    # Initialize the OpenAI client
    client = OpenAI()

    try:
        # Create a speech file from the text
        speech_file_path = "speech_output.mp3"
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)

        # Save the audio file
        response.write_to_file(speech_file_path)
        print(f"✅ Speech saved to {speech_file_path}")

        # Play the audio file (Windows)
        os.system(f"start {speech_file_path}")

    except Exception as e:
        print(f"❌ Error generating speech: {str(e)}")


def analyze_image(image_path, question, speak=True, voice="echo"):
    """Send an image to OpenAI's API for analysis"""
    # Check if the OPENAI_API_KEY environment variable is set
    api_key = "REMOVED_KEY"

    # Initialize the OpenAI client
    client = OpenAI()

    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"❌ Image file '{image_path}' not found.")
        return

    print(f"📤 Sending image '{image_path}' to OpenAI for analysis...")
    print(f"🔍 Question: {question}")

    try:
        # Encode the image
        base64_image = encode_image(image_path)

        # Send request to OpenAI's API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o which has vision capabilities
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )

        # Extract and print the analysis
        analysis = response.choices[0].message.content
        print("\n✅ Analysis from OpenAI:")
        print("=" * 50)
        print(analysis)
        print("=" * 50)

        # Convert the analysis to speech if requested
        if speak:
            speak_text(analysis, voice)

        return analysis

    except Exception as e:
        print(f"❌ Error communicating with OpenAI API: {str(e)}")
        return None


if __name__ == "__main__":
    # Default values
    image_path = "droidcam_screenshot.jpg"
    question = "What do we see here?"
    speak = True
    voice = "echo"  # Options: alloy, echo, fable, onyx, nova, shimmer
    # alloy: Neutral, balanced voice
    # echo: Expressive, versatile voice (default)
    # fable: Expressive, storyteller voice
    # onyx: Deep, authoritative voice
    # nova: Warm, friendly voice
    # shimmer: Clear, crisp voice

    # Allow command line arguments to override defaults
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    if len(sys.argv) > 2:
        question = sys.argv[2]
    if len(sys.argv) > 3:
        # If the third argument is "false" or "no", disable speech
        speak = sys.argv[3].lower() not in ("false", "no", "0", "disable", "off")
    if len(sys.argv) > 4:
        voice = sys.argv[4]

    analyze_image(image_path, question, speak, voice)
