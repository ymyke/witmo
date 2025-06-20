import os
import json
from loguru import logger
from tui.io import tt

class History:
    def __init__(self, file_location: str, file_name: str = "chat_history.json"):
        self.file_path = os.path.join(file_location, file_name)
        if not os.path.exists(file_location):
            os.makedirs(file_location)
            logger.info(f"Created directory: {file_location}")
        self.messages = []

    def load(self):
        if not os.path.exists(self.file_path):
            logger.info("No previous chat history found, starting fresh")
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.messages = [
                msg
                for msg in loaded
                if isinstance(msg, dict)
                and "role" in msg
                and "content" in msg
                and (
                    isinstance(msg["content"], str) or isinstance(msg["content"], list)
                )
            ]
            logger.info(
                f"Loaded existing chat history with {len(self.messages)} messages"
            )
            skipped_count = len(loaded) - len(self.messages)
            if skipped_count > 0:
                logger.warning(
                    f"Skipped {skipped_count} invalid messages in chat history"
                )
        except json.JSONDecodeError:
            logger.warning(
                "Chat history file was corrupted, starting with empty history"
            )
            self.messages = []

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
            logger.success(f"Chat history saved to {self.file_path}")
        except Exception as e:
            logger.error(f"Error saving chat history: {str(e)}")

    def append(self, message):
        self.messages.append(message)

    def last(self, n=10):
        return self.messages[-n:]

    def __len__(self):
        return len(self.messages)

    def __enter__(self):
        self.load()
        tt(f"Loaded chat history with {len(self.messages)} messages")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
        tt(f"Saved chat history with {len(self.messages)} messages")
        return False
