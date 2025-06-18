import os
import argparse
import json
from loguru import logger
from slugify import slugify
from llm import system_prompt
from llm.history import History
from spoilers import parse_spoiler_args, generate_spoiler_prompt
from tui.print_wrapped import pw
from camera.camera_protocol import CameraProtocol


class Session:
    def __init__(
        self,
        game_name,
        game_name_slug,
        output_dir,
        system_prompt,
        history,
        camera: CameraProtocol,
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
        self.camera: CameraProtocol = camera
        self.prompts = prompts  # dict of prompts for the current game
        self.spoiler_settings = spoiler_settings
        self.do_crop = do_crop

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Session":

        logger.debug("Creating a new session from command line arguments...")

        # Names and directories:
        logger.debug("Setting up game name and output directory...")
        game_name_slug = slugify(args.game_name)
        output_dir = os.path.join("history", game_name_slug) # TODO
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Spoiler settings:
        logger.debug("Parsing spoiler settings...")
        spoiler_settings = parse_spoiler_args(args.spoilers)
        spoiler_prompt = generate_spoiler_prompt(spoiler_settings)

        # System prompt:
        logger.debug("Generating system prompt...")
        sysprompt = system_prompt.prompt.format(
            game_name=args.game_name, spoiler_prompt=spoiler_prompt
        )
        logger.debug(f"System prompt:\n{sysprompt}")

        # History:
        logger.debug("Loading chat history...")
        history = History(output_dir)
        history.load()

        # Camera:
        logger.debug("Initializing camera...")
        if args.no_camera:
            logger.info("Running in no-camera mode.")
            from camera.no_camera import NoCamera

            camera = NoCamera()
        elif args.test_camera:
            logger.info("Using TestCamera for local testing.")
            from camera.test_camera import TestCamera

            camera = TestCamera(args.delete_remote, output_dir)
        else:
            from camera.adb_camera import AdbCamera

            camera = AdbCamera(args.delete_remote, output_dir)

        # Prompts:
        logger.debug("Loading prompts...")
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
