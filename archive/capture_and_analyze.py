import os
import cv2  # Still needed for compatibility elsewhere
import time
import base64  # Still needed for compatibility elsewhere
import datetime  # Still needed for compatibility elsewhere
import json
import argparse
import sys
from openai import OpenAI
import keyboard
import pygame
import image_capture

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Interactive Game Coach')
parser.add_argument('game_name', nargs='?', default='Unspecified Game', 
                    help='Name of the game being played')
args = parser.parse_args()

# --- CONFIG ---
ip = "192.168.1.109"
stream_url = f"http://{ip}:8080/videofeed"
# Create game-specific output directory
game_name_safe = args.game_name.replace(" ", "_").lower()
output_dir = os.path.join("game_coach_captures", game_name_safe)
history_file = os.path.join(output_dir, "history.json")

# Initialize the OpenAI client
client = OpenAI(api_key="REMOVED_KEY")

# Initialize pygame for audio playback
pygame.init()
pygame.mixer.init()

# Create an ImageCapture instance
image_capturer = image_capture.ImageCapture(stream_url, output_dir)

# Key mappings for different gaming coach prompts
KEY_PROMPTS = {
    "space": f"{args.game_name}: Describe what we see here in detail and explain all game mechanics that are important.",
"m": f"{args.game_name}: What are things I definitely must not have missed in the part of the map I am now?",
"f": f"{args.game_name}: What are some reasonable things to do next from here in the map/game?",
"s": f"{args.game_name}: Explain the numbers and stats we see here in detail. Is this a better weapon or item than what I currently have?",
}

def ensure_dirs():
    """Ensure required directories exist"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ Created directory: {output_dir}")

def capture_image():
    """Capture an image from the configured video stream"""
    return image_capturer.capture()

def encode_image(image_path):
    """Encode an image to base64 for API transmission"""
    return image_capture.encode_image_to_base64(image_path)

def analyze_image(image_path, question):
    """Send an image to OpenAI's API for analysis"""
    print(f"📤 Sending gameplay to AI coach...")
    print(f"🔍 Analysis request: {question}")
    
    try:
        # Create a detailed prompt for gaming coaching
        system_message = f"""You are an expert gaming coach for {args.game_name}. 
Your job is to analyze gameplay images and provide helpful, concise advice.
Focus ONLY on what's happening in the game.
Format your responses in short, clear paragraphs.
Be specific and actionable - tell the player exactly what to do next.
"""
        
        # Encode the image
        base64_image = encode_image(image_path)
        
        # Send request to OpenAI's API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o which has vision capabilities
            messages=[
                {
                    "role": "system", 
                    "content": system_message
                },
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
        
        # Extract the analysis
        analysis = response.choices[0].message.content
        print("\n✅ Analysis from OpenAI:")
        print("=" * 50)
        print(analysis)
        print("=" * 50)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error communicating with OpenAI API: {str(e)}")
        return f"Error analyzing image: {str(e)}"

def speak_text(text, voice="echo"):
    """Convert text to speech using OpenAI's TTS API and play it using pygame"""
    print(f"🔊 Converting text to speech using voice: {voice}...")
    
    # Create a speech file from the text
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    speech_file_path = os.path.join(output_dir, f"speech_{timestamp}.mp3")
    
    try:
        # Generate speech from text
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        
        # Save the audio file
        response.write_to_file(speech_file_path)
        print(f"✅ Speech saved to {speech_file_path}")
        
        # Play the audio file using pygame
        print(f"🔊 Playing audio response...")
        
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Load and play the audio file
        pygame.mixer.music.load(speech_file_path)
        pygame.mixer.music.play()
        
        # Estimate speech duration based on word count (rough approximation)
        words = len(text.split())
        wait_time = max(3, min(30, words * 0.5))  # At least 3 seconds, at most 30
        
        # Wait for the audio to finish playing
        time.sleep(wait_time)
        
        return speech_file_path
        
    except Exception as e:
        print(f"❌ Error generating speech: {str(e)}")
        return speech_file_path  # Return the path even if there was an error

def save_to_history(image_path, prompt, response, audio_path):
    """Save the capture details to history"""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "image_path": image_path,
        "prompt": prompt,
        "response": response,
        "audio_path": audio_path
    }
    
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ History file was corrupted, creating new history")
    
    history.append(entry)
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved interaction to history file")

def list_prompt_options():
    """Display available prompt options"""
    print("\n=== Gaming Coach Commands ===")
    print(f"Game: {args.game_name}")
    for key, prompt in KEY_PROMPTS.items():
        # Extract the first part of the prompt before the game name
        short_desc = prompt.split(f"in {args.game_name}")[0].strip()
        if not short_desc.endswith("?"):
            short_desc += " "
        print(f"[{key}] - {short_desc}")
    print("[Esc] - Exit program")
    print("\nPress a key to capture and analyze your gameplay...")

def main():
    """Main program loop"""
    print("\n" + "="*60)
    print("🎮 INTERACTIVE GAME COACH 🎮".center(60))
    print("="*60)
    print(f"GAME: {args.game_name}".center(60))
    print("-"*60)
    print("• Capture your gameplay and get real-time coaching advice")
    print("• Press different keys for specific coaching guidance")
    print("• Audio feedback will play automatically")
    print("-"*60)
    
    ensure_dirs()
    list_prompt_options()
    
    while True:
        # Wait for a key press
        event = keyboard.read_event(suppress=True)
        
        # Process only on key down events
        if event.event_type == 'down':
            if event.name == 'esc':
                print("\n👋 Thanks for using Game Coach! Exiting program...")
                break
                
            # Check if the pressed key has a defined prompt
            if event.name in KEY_PROMPTS:
                prompt = KEY_PROMPTS[event.name]
                print(f"\n🔑 Command activated: '{event.name}'")
                
                # Capture image
                image_path = capture_image()
                if not image_path:
                    print("❌ Failed to capture gameplay. Is your camera/feed working?")
                    continue
                
                print("🕹️ Analyzing your gameplay situation...")
                
                # Analyze image
                response = analyze_image(image_path, prompt)
                
                print("\n🎯 COACH ADVICE:")
                print("-"*60)
                print(response)
                print("-"*60)
                
                # Convert to speech and play
                audio_path = speak_text(response)
                
                # Save to history
                save_to_history(image_path, prompt, response, audio_path)
                
                # Wait a bit before accepting next keypress
                time.sleep(1)
                list_prompt_options()
            else:
                print(f"⚠️ No coaching command defined for key '{event.name}'")

def display_example_usage():
    """Display example usage information"""
    print("\nExample Usage:")
    print("-------------")
    print("python capture_and_analyze.py \"Elden Ring\"")
    print("python capture_and_analyze.py Minecraft")
    print("python capture_and_analyze.py \"Call of Duty: Warzone\"")
    print("\nConnect your phone camera using IP Webcam or similar app")
    print("Set the IP address in the script if different from the default")

if __name__ == "__main__":
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("\n⚠️ No game name provided. Please specify the game name.")
        display_example_usage()
        sys.exit(1)
        
    main()
