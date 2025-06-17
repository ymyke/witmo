import os
import argparse
from loguru import logger
from history import History
from slugify import slugify
import system_prompt
import json
from spoilers import parse_spoiler_args, generate_spoiler_prompt
from print_utils import pw
from image import BasicImage, CroppedImage, Image


class Session:
    def __init__(
        self,
        game_name,
        game_name_slug,
        output_dir,
        system_prompt,
        history,
        camera,
        prompts,
        spoiler_settings,
        do_crop=False,
    ):
        # TODO simpify this constructor?
        self.game_name = game_name
        self.game_name_slug = game_name_slug
        self.output_dir = output_dir
        self.system_prompt = system_prompt
        self.history = history
        self.camera = camera
        self.prompts = prompts  # dict of prompts for the current game
        self.spoiler_settings = spoiler_settings
        self.do_crop = do_crop

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Session":

        # Names and directories:
        game_name_slug = slugify(args.game_name)
        output_dir = os.path.join("history", game_name_slug)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Spoiler settings:
        spoiler_settings = parse_spoiler_args(args.spoilers)
        spoiler_prompt = generate_spoiler_prompt(spoiler_settings)

        # System prompt:
        sysprompt = system_prompt.prompt.format(
            game_name=args.game_name, spoiler_prompt=spoiler_prompt
        )
        logger.debug(f"System prompt:\n{sysprompt}")

        # History:
        history = History(output_dir)
        history.load()

        # Camera:
        if args.no_camera:
            logger.info("Running in no-camera mode.")
            from no_camera import NoCamera

            camera = NoCamera()
        elif args.test_camera:
            logger.info("Using TestCamera for local testing.")
            from test_camera import TestCamera

            camera = TestCamera(args.delete_remote, output_dir)
        else:
            from adb_camera import AdbCamera

            camera = AdbCamera(args.delete_remote, output_dir)

        # Prompts:
        with open("prompt_map.json", "r", encoding="utf-8") as f:
            promptmap = json.load(f)
        promptlist = promptmap.get(game_name_slug, [])
        promptsdir = {
            item["key"]: item for item in sorted(promptlist, key=lambda x: x["key"])
        }
        if not promptsdir:
            logger.warning(
                f"No prompts found for game '{args.game_name}'. "
                "You can add them to 'prompt_map.json'."
            )
        else:
            pw(f"Loaded {len(promptsdir)} prompts for game '{args.game_name}'.")

        # Whether to crop the images:
        do_crop = getattr(args, "crop", False)

        # Return a new Session instance:
        return cls(
            args.game_name,
            game_name_slug,
            output_dir,
            sysprompt,
            history,
            camera,
            promptsdir,
            spoiler_settings,
            do_crop=do_crop,
        )
