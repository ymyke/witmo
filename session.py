import os
import argparse
from loguru import logger
from history import History
from slugify import slugify
import system_prompt


class Session:
    def __init__(self, game_name, game_name_safe, output_dir, system_prompt, history, camera):
        self.game_name = game_name
        self.game_name_safe = game_name_safe
        self.output_dir = output_dir
        self.system_prompt = system_prompt
        self.history = history
        self.camera = camera

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Session":
        game_name_safe = slugify(args.game_name)
        output_dir = os.path.join("history", game_name_safe)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        sysprompt = system_prompt.prompt.format(game_name=args.game_name)

        history = History(output_dir)
        history.load()

        if args.test_camera:
            logger.info("Using TestCamera for local testing.")
            from test_camera import TestCamera

            camera = TestCamera(args.delete_remote, output_dir)
        else:
            from adb_camera import AdbCamera

            camera = AdbCamera(args.delete_remote, output_dir)

        return cls(args.game_name, game_name_safe, output_dir, sysprompt, history, camera)
