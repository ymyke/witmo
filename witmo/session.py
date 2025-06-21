import os
import argparse
import json
from loguru import logger
from slugify import slugify
from witmo.llm import system_prompt
from witmo.llm.history import History
from witmo.llm.models import ModelManager
from witmo.spoilers import parse_spoiler_args, generate_spoiler_prompt
from witmo.tui.io import tt
from witmo.tui.audio import AudioMode
from witmo.camera.camera_protocol import CameraProtocol


class Session:
    game_name: str
    game_name_slug: str
    history_location: str
    output_dir: str
    spoiler_prompt: str
    system_prompt: str
    history: History
    camera: CameraProtocol
    prompts: dict[str, dict]
    do_crop: bool
    audio_mode: AudioMode
    model_manager: ModelManager

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Session":
        obj = cls()

        logger.debug("Creating a new session from command line arguments...")

        # Names and directories:
        logger.debug("Setting up game name and output directory...")
        obj.history_location = "history"
        obj.game_name = args.game_name.strip()
        obj.game_name_slug = slugify(args.game_name)
        obj.output_dir = os.path.join(obj.history_location, obj.game_name_slug)
        if not os.path.exists(obj.output_dir):
            os.makedirs(obj.output_dir)

        # Spoiler settings:
        logger.debug("Parsing spoiler settings...")
        obj.spoiler_prompt = generate_spoiler_prompt(parse_spoiler_args(args.spoilers))

        # System prompt:
        logger.debug("Generating system prompt...")
        obj.system_prompt = system_prompt.prompt.format(
            game_name=args.game_name, spoiler_prompt=obj.spoiler_prompt
        )
        logger.debug(f"System prompt:\n{obj.system_prompt}")

        # History:
        logger.debug("Loading chat history...")
        obj.history = History(obj.output_dir)

        # Camera:
        logger.debug("Initializing camera...")
        if args.no_camera:
            logger.info("Running in no-camera mode.")
            from witmo.camera.no_camera import NoCamera

            obj.camera = NoCamera()
        elif args.test_camera:
            logger.info("Using TestCamera for local testing.")
            from witmo.camera.test_camera import TestCamera

            obj.camera = TestCamera(obj.output_dir)
        else:
            from witmo.camera.adb_camera import AdbCamera

            obj.camera = AdbCamera(args.delete_remote, obj.output_dir)

        # Prompts:
        logger.debug("Loading prompts...")
        with open("prompt_map.json", "r", encoding="utf-8") as f:
            promptmap = json.load(f)
        promptlist = promptmap.get(obj.game_name_slug, [])
        if not promptlist:
            msg = f"No prompts found for game '{args.game_name}'. Trying default prompts."
            logger.warning(msg)
            tt(msg, style="warning")
            promptlist = promptmap.get("default", [])
        if not promptlist:
            msg = "No default prompts found either. Check 'prompt_map.json'."
            logger.warning(msg)
            tt(msg, style="error")
        obj.prompts = {
            item["key"]: item for item in sorted(promptlist, key=lambda x: x["key"])
        }
        if obj.prompts:
            tt(f"Loaded {len(obj.prompts)} prompts for game '{args.game_name}'.")

        # Whether to crop the images:
        obj.do_crop = getattr(args, "crop", False)

        # Audio mode:
        obj.audio_mode = AudioMode(getattr(args, "audio_mode", "off"))

        # Set up model manager:
        logger.debug("Setting up model manager...")
        obj.model_manager = ModelManager()
        obj.model_manager.set_current_model_by_key("3")

        return obj
