import os
import cv2
import time
import base64
import datetime
import json
from openai import OpenAI
import keyboard
import vlc

# --- CONFIG ---
ip = "192.168.1.109"
stream_url = f"http://{ip}:8080/videofeed"
output_dir = "interactive_captures"
history_file = os.path.join(output_dir, "history.json")

# Initialize the OpenAI client
client = OpenAI(api_key="REMOVED_KEY")

# Key mappings for different prompts
KEY_PROMPTS = {
    "space": "Describe what you see on the TV screen.",
    "r": "Read any text visible on the TV screen.",
    "d": "Describe the main scene or visual elements shown on the TV screen in detail.",
    "p": "Who are the people shown on the TV screen and what are they doing?",
    "t": "What is the title or name of the content shown on the TV screen?",
    "g": "What genre of content is showing on the TV screen?",
    "e": "What emotions are being conveyed by the content on the TV screen?",
    "m": "Describe any motion or action happening on the TV screen."
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
    print(f"📤 Sending image to OpenAI for analysis...")
    print(f"🔍 Question: {question}")
    
    try:
        # Enhance the prompt to focus only on the TV content
        enhanced_question = f"{question} Focus ONLY on the TV contents and nothing else in the image."
        
        # Encode the image
        base64_image = encode_image(image_path)
        
        # Send request to OpenAI's API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o which has vision capabilities
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": enhanced_question},
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
    
    try:
        # Create a speech file from the text
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        speech_file_path = os.path.join(output_dir, f"speech_{timestamp}.mp3")
        
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        
        # Save the audio file
        response.write_to_file(speech_file_path)
        print(f"✅ Speech saved to {speech_file_path}")
        
        # Play the audio file (Windows)
        # os.system(f'start {speech_file_path}')
        player = vlc.MediaPlayer(speech_file_path)
        player.play()
        # wait until the music starts
        time.sleep(0.5)
        # keep the script alive while it's playing
        while player.is_playing():
            time.sleep(0.1)

        
        return speech_file_path
        
    except Exception as e:
        print(f"❌ Error generating speech: {str(e)}")
        return None

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
    print("\n=== Available Prompt Options ===")
    for key, prompt in KEY_PROMPTS.items():
        print(f"[{key}] - {prompt}")
    print("[Esc] - Exit program")
    print("\nWaiting for keypress...")

def main():
    """Main program loop"""
    print("📷 Interactive Capture & Analyze 📷")
    print("Press a key to capture and analyze an image")
    
    ensure_dirs()
    list_prompt_options()
    
    while True:
        # Wait for a key press
        event = keyboard.read_event(suppress=True)
        
        # Process only on key down events
        if event.event_type == 'down':
            if event.name == 'esc':
                print("👋 Exiting program...")
                break
                
            # Check if the pressed key has a defined prompt
            if event.name in KEY_PROMPTS:
                prompt = KEY_PROMPTS[event.name]
                print(f"\n🔑 Key pressed: '{event.name}'")
                
                # Capture image
                image_path = capture_image()
                if not image_path:
                    continue
                
                # Analyze image
                response = analyze_image(image_path, prompt)
                
                # Convert to speech and play
                audio_path = speak_text(response)
                
                # Save to history
                save_to_history(image_path, prompt, response, audio_path)
                
                # Wait a bit before accepting next keypress
                time.sleep(1)
                list_prompt_options()
            else:
                print(f"⚠️ No prompt defined for key '{event.name}'")

if __name__ == "__main__":
    main()
