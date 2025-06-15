import os
import argparse
from history import History


class Session:
    def __init__(self, game_name, output_dir, system_prompt, history):
        self.game_name = game_name
        self.output_dir = output_dir
        self.system_prompt = system_prompt
        self.history = history

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Session":
        # TODO use slugify
        game_name_safe = args.game_name.replace(" ", "_").lower()
        output_dir = os.path.join("history", game_name_safe)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # TODO get from file
        system_prompt = f"""
    You are an expert gaming assistant for {args.game_name}.
    Your job is to analyze gameplay images and provide helpful, concise advice.
    Focus ONLY on what's happening in the game.
    Be specific and actionable, clear and concise.
    Never just read what you see on the screen, assume that the user can read it themselves.
    """
        history = History(output_dir)
        history.load()
        return cls(args.game_name, output_dir, system_prompt, history)
