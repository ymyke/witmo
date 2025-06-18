import os
import sys
import uuid
from loguru import logger
import tempfile
import threading
from print_utils import pw
from .openai_client import openai_client


def speak_text(text: str, voice: str = "alloy") -> None:
    """Convert text to speech using OpenAI's TTS API and play it using pygame
    (non-blocking).
    """

    def _tts_and_play(text: str, voice: str) -> None:
        try:
            response = openai_client.audio.speech.create(
                model="tts-1", voice=voice, input=text
            )
            dir_ = tempfile.gettempdir()
            filename = f"{uuid.uuid4()}.mp3"
            path = os.path.join(dir_, filename)
            logger.debug(f"Saving TTS response to {path}")
            response.write_to_file(path)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            logger.error(f"TTS error: {e}")

    # Import pygame only when we need it:
    if not "pygame" in sys.modules:
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        import pygame

    pw("Generating and playing voice output in the background...")
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    threading.Thread(target=_tts_and_play, args=(text, voice), daemon=True).start()
