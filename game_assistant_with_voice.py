import os
import cv2
import time
import base64
import datetime
import json
import argparse
import sys
from openai import OpenAI
import pygame
import threading
import speech_recognition as sr

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Interactive Game Assistant with Chat')
parser.add_argument('game_name', nargs='?', default='Unspecified Game', 
                    help='Name of the game being played')
parser.add_argument('--voice-mode', action='store_true', 
                    help='Enable voice interaction mode')
parser.add_argument('--ip', default='192.168.1.109',
                    help='IP address of the video feed')
parser.add_argument('--image', 
                    help='Path to an initial image to analyze instead of capturing one')
args = parser.parse_args()

# --- CONFIG ---
stream_url = f"http://{args.ip}:8080/videofeed"
# Create game-specific output directory
game_name_safe = args.game_name.replace(" ", "_").lower()
output_dir = os.path.join("game_coach_captures", game_name_safe)
history_file = os.path.join(output_dir, "chat_history.json")

# Initialize the OpenAI client
client = OpenAI(api_key="REMOVED_KEY")

# Initialize pygame for audio playback
pygame.init()
pygame.mixer.init()

# Initialize speech recognition
recognizer = sr.Recognizer()

# Chat context to maintain conversation history
chat_context = []

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
    print(f"📤 Sending gameplay to AI assistant...")
    print(f"🔍 Analysis request: {question}")
    
    try:
        # Create a detailed prompt for gaming assistant
        system_message = f"""You are an expert gaming assistant for {args.game_name}. 
Your job is to analyze gameplay images and provide helpful, concise advice.
Focus ONLY on what's happening in the game.
Format your responses in short, clear paragraphs.
Be specific and actionable - tell the player exactly what to do next.
"""
        
        # Encode the image
        base64_image = encode_image(image_path)
        
        # Prepare messages including chat history for context
        messages = [
            {
                "role": "system", 
                "content": system_message
            }
        ]
        
        # Add chat history for context (limited to last 10 messages)
        for msg in chat_context[-10:]:
            messages.append(msg)
            
        # Add the current question with image
        messages.append({
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
        })
        
        # Send request to OpenAI's API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o which has vision capabilities
            messages=messages,
            max_tokens=1000,
        )
        
        # Extract the analysis
        analysis = response.choices[0].message.content
        print("\n✅ Analysis from AI Assistant:")
        print("=" * 50)
        print(analysis)
        print("=" * 50)
        
        # Update chat context
        chat_context.append({
            "role": "user",
            "content": [{"type": "text", "text": question}]
        })
        
        chat_context.append({
            "role": "assistant",
            "content": analysis
        })
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error communicating with OpenAI API: {str(e)}")
        return f"Error analyzing image: {str(e)}"

def speak_text(text, voice="alloy"):
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
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        return speech_file_path
        
    except Exception as e:
        print(f"❌ Error generating speech: {str(e)}")
        return speech_file_path  # Return the path even if there was an error

def listen_for_voice():
    """Listen for voice input from the microphone"""
    print("🎤 Listening for voice input... (speak now)")
    
    with sr.Microphone() as source:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)
        
        try:
            # Listen for audio input
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            
            # Convert speech to text
            text = recognizer.recognize_google(audio)
            print(f"🔊 You said: {text}")
            
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ Timeout: No speech detected")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error during voice recognition: {e}")
            return None

def chat_with_ai(initial_image_path=None):
    """Start an interactive chat session with the AI assistant"""
    global chat_context
    
    print("\n" + "="*60)
    print("💬 STARTING INTERACTIVE CHAT SESSION 💬".center(60))
    print("="*60)
    print("• Type 'exit', 'quit', or 'bye' to end the chat")
    print("• Type 'capture' to take a new screenshot")
    print("• Type your questions or messages normally")
    if args.voice_mode:
        print("• Say 'goodbye' to end the voice chat")
        print("• Say 'capture' to take a new screenshot")
    print("-"*60)
    
    # If we have an initial image, start with that
    if initial_image_path:
        initial_prompt = f"{args.game_name}: Describe what we see here and help me understand what's happening. Do not just read out what is there. I can read the screen myself. Focus on giving me insights, help me understand, provide truly useful information."
        response = analyze_image(initial_image_path, initial_prompt)
        speak_text(response)
    
    # Main chat loop
    while True:
        # Get user input (voice or text)
        if args.voice_mode:
            print("\n🎤 Speak your question or command...")
            user_input = listen_for_voice()
            
            # If voice recognition failed, fall back to text input
            if not user_input:
                print("🔄 Falling back to text input...")
                user_input = input("\n💬 Your message: ")
        else:
            user_input = input("\n💬 Your message: ")
        
        # Check for exit commands
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("👋 Ending chat session. Thanks for using the Interactive Game Assistant!")
            break
            
        # Check for capture command
        if user_input.lower() == 'capture':
            print("🔄 Capturing new gameplay image...")
            new_image_path = capture_image()
            
            if new_image_path:
                # Ask for what to analyze in the new image
                if args.voice_mode:
                    print("\n🎤 What would you like to know about this gameplay moment?")
                    follow_up = listen_for_voice()
                    if not follow_up:
                        follow_up = "Describe what we see here and help me understand what's happening."
                else:
                    follow_up = input("\n❓ What would you like to know about this gameplay moment? ")
                    if not follow_up.strip():
                        follow_up = "Describe what we see here and help me understand what's happening."
                
                # Analyze the new image
                response = analyze_image(new_image_path, follow_up)
                speak_text(response)
                continue
            else:
                print("❌ Failed to capture new image. Continuing chat with previous context.")
                continue
                
        # Normal chat interaction - no image for this message
        print(f"💬 Sending message to AI assistant...")
        
        try:
            # Prepare system message
            system_message = f"""You are an expert gaming assistant for {args.game_name}. 
            You're having a conversation with the player about their gameplay.
            Be helpful, concise, and specific with your advice."""
            
            # Prepare messages including chat history
            messages = [
                {
                    "role": "system", 
                    "content": system_message
                }
            ]
            
            # Add chat history (limited to last 10 messages)
            for msg in chat_context[-10:]:
                messages.append(msg)
                
            # Add the current question
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Send request to OpenAI's API
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=messages,
                max_tokens=1000,
            )
            
            # Extract the response
            ai_response = response.choices[0].message.content
            
            # Update chat context
            chat_context.append({"role": "user", "content": user_input})
            chat_context.append({"role": "assistant", "content": ai_response})
            
            # Display and speak the response
            print("\n✅ AI Assistant:")
            print("-" * 60)
            print(ai_response)
            print("-" * 60)
            
            # Convert to speech
            speak_text(ai_response)
            
        except Exception as e:
            print(f"❌ Error in chat: {str(e)}")
            ai_response = "Sorry, I encountered a problem processing your request. Can you try again?"
            print(ai_response)
            speak_text(ai_response)

def save_chat_history():
    """Save the chat history to a file"""
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(chat_context, f, indent=2, ensure_ascii=False)
        print(f"✅ Chat history saved to {history_file}")
    except Exception as e:
        print(f"❌ Error saving chat history: {str(e)}")

def load_chat_history():
    """Load existing chat history if available"""
    global chat_context
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                chat_context = json.load(f)
            print(f"✅ Loaded existing chat history with {len(chat_context)} messages")
        except json.JSONDecodeError:
            print("⚠️ Chat history file was corrupted, starting with empty history")
            chat_context = []
    else:
        print("ℹ️ No previous chat history found, starting fresh")
        chat_context = []

def main():
    """Main program flow"""
    print("\n" + "="*60)
    print("🎮 INTERACTIVE GAME ASSISTANT 🎮".center(60))
    print("="*60)
    print(f"GAME: {args.game_name}".center(60))
    print("-"*60)
    print("• Capture gameplay, get advice, and chat with your AI assistant")
    print("• Conversation history is maintained for context")    
    if args.voice_mode:
        print("• Voice interaction mode ENABLED")
    print("-"*60)
    
    ensure_dirs()
    load_chat_history()
    
    try:
        # Check if initial image was provided via command-line argument
        if args.image:
            if os.path.exists(args.image):
                print(f"\n🖼️ Using provided image: {args.image}")
                initial_image = args.image
                chat_with_ai(initial_image)
            else:
                print(f"\n⚠️ The specified image file does not exist: {args.image}")
                print("Falling back to capturing a new image...")
                # Initial capture to start the conversation
                print("\n🎮 Let's start by capturing your current gameplay")
                initial_image = capture_image()
                
                if initial_image:
                    # Begin interactive chat with the initial image
                    chat_with_ai(initial_image)
                else:
                    print("\n⚠️ Could not capture initial gameplay image.")
                    print("Starting chat without an image...")
                    chat_with_ai()
        else:
            # Initial capture to start the conversation
            print("\n🎮 Let's start by capturing your current gameplay")
            initial_image = capture_image()
            
            if initial_image:
                # Begin interactive chat with the initial image
                chat_with_ai(initial_image)
            else:
                print("\n⚠️ Could not capture initial gameplay image.")
                print("Starting chat without an image...")
                chat_with_ai()
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Program interrupted by user")
    finally:
        # Save chat history before exiting
        save_chat_history()
        print("\n👋 Thanks for using Interactive Game Assistant! Exiting program...")

def display_example_usage():
    """Display example usage information"""
    print("\nExample Usage:")
    print("-------------")
    print("python interactive_game_assistant.py \"Elden Ring\"")
    print("python interactive_game_assistant.py Minecraft --voice-mode")
    print("python interactive_game_assistant.py \"Call of Duty: Warzone\" --ip 192.168.1.100")
    print("python interactive_game_assistant.py \"Elden Ring\" --image game_coach_captures/elden_ring/capture_20250612_215322.jpg")
    print("\nConnect your phone camera using IP Webcam or similar app")
    print("Set the IP address with --ip if different from the default")
    print("Use --image to analyze an existing image instead of capturing one")

if __name__ == "__main__":
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("\n⚠️ No game name provided. Please specify the game name.")
        display_example_usage()
        sys.exit(1)
        
    main()
