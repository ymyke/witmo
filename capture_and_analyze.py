import os
import cv2
import time
import base64
import datetime
import json
import argparse
import sys
from openai import OpenAI
import keyboard
import vlc

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

# Key mappings for different gaming coach prompts
KEY_PROMPTS = {
    "space": f"What's happening in {args.game_name} right now? Provide a quick overview.",
    "s": f"What strategy should I use in this situation in {args.game_name}?",
    "o": f"What are my objectives or goals at this point in {args.game_name}?",
    "t": f"Explain the game mechanics visible on screen in {args.game_name}.",
    "i": f"Identify any items, weapons, or resources I should collect in {args.game_name}.",
    "e": f"What enemies or obstacles am I facing in {args.game_name} and how should I approach them?",
    "h": f"Any hints or tips for this section of {args.game_name}?",
    "p": f"What's the optimal path or approach from here in {args.game_name}?",
    "c": f"Explain the controls or commands I should use in {args.game_name} for this situation.",
    "d": f"Debug what I'm doing wrong in {args.game_name} and suggest improvements."
}

def ensure_dirs():
    """Ensure required directories exist"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ Created directory: {output_dir}")

def capture_image():
    """Capture an image from the configured video stream"""
    print("📸 Capturing image from stream...")
    
    cap = cv2.VideoCapture(stream_url)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Failed to grab frame from video feed")
        return None
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"capture_{timestamp}.jpg")
    cv2.imwrite(filename, frame)
    print(f"✅ Frame captured and saved as '{filename}'")
    
    return filename

def encode_image(image_path):
    """Encode an image to base64 for API transmission"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

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
Limit your response to 2-3 paragraphs maximum."""
        
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
    """Convert text to speech using OpenAI's TTS API and play it"""
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
        
        # Play the audio file using command line
        print(f"🔊 Playing audio response...")
        
        # Estimate speech duration based on word count (rough approximation)
        words = len(text.split())
        wait_time = max(3, min(30, words * 0.5))  # At least 3 seconds, at most 30
        
        # Use os.system instead of VLC module to avoid errors
        os.system(f'start {speech_file_path}')
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
