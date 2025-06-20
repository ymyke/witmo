import os
import sys
import threading
import uuid
import tempfile
from loguru import logger

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame


def play_soundfile(path: str):
    """Play a sound file (mp3) in the background using pygame."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    def _play():
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            logger.error(f"Sound playback error: {e}")

    threading.Thread(target=_play, daemon=True).start()


def play_ding():
    """Play a ding sound."""
    sound_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",  # FIXME not really robust if file structure changes
            "assets",
            "sounds",
            "copper-bell-ding-2-214922.mp3",
        )
    )
    play_soundfile(sound_path)


def speak_text(text: str, voice: str = "alloy") -> None:
    """Convert text to speech using OpenAI's TTS API and play it."""

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
            play_soundfile(path)  # Thread in a thread...
        except Exception as e:
            logger.error(f"TTS error: {e}")

    if "openai_client" not in sys.modules:
        from llm.openai_client import openai_client
    threading.Thread(target=_tts_and_play, args=(text, voice), daemon=True).start()


class AudioMode:
    """Manage audio modes."""

    MODES = ["off", "ding", "voice", "both"]

    def __init__(self, mode: str = "off"):
        if mode not in self.MODES:
            mode = "off"
        self.mode = mode

    def cycle(self):
        idx = self.MODES.index(self.mode)
        self.mode = self.MODES[(idx + 1) % len(self.MODES)]

    def should_ding(self) -> bool:
        return self.mode in ("ding", "both")

    def should_voice(self) -> bool:
        return self.mode in ("voice", "both")

    def __str__(self):
        return self.mode
