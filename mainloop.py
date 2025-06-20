from image import CroppedImage, BasicImage, Image
from session import Session
from readchar import readkey, key
from llm.completion import generate_completion
from tui import select_prompt
from tui import select_llm
from tui.io import (
    tt,
    tp,
    menu_panel,
    request_panel,
    response_panel,
    get_textinput,
    dot_animation,
    background_animation,
)
from tui.audio import play_ding, speak_text


main_menu = [
    ("space", "capture a new image"),
    ("enter", "enter free-text prompt"),
    ("", ""),
    ("p", "pick preconfigured prompt and send it"),
    ("c", "show latest capture again"),
    ("m", "select LLM"),
    ("a", "cycle audio mode"),
    ("esc", "quit"),
]


def mainloop(session: Session, initial_image: BasicImage | None = None) -> None:
    """Main interactive loop for the application.

    Behavior:
    - If initial_image is provided, the loop will immediately use it as the image for
      the first prompt selection, skipping the manual and image capture step.
    - Otherwise, the user is prompted to capture a new image, start a chat without an
      image, or quit.
    """

    last_image: Image | None = None  # Save the last capture so it can be shown again
    suppress_menu = False  # Suppress the main menu in certain cases
    while True:

        # Setup, show menu, handle special case where initial_image is provided:
        prompt = None
        image: Image | None = None
        if initial_image:
            image = initial_image
            k = key.SPACE
        else:
            tt()
            if not suppress_menu:
                tt(menu_panel("Main menu", main_menu, "top"))
                state_str = (
                    f"[Audio: {session.audio_mode.mode.upper()} • "
                    f"LLM: {session.model_manager.current_model.shortname} • "
                    f"Crop: {'ON' if session.do_crop else 'OFF'}]"
                )
                tt(state_str)
            k = readkey()
        suppress_menu = False

        # Handle the different keys:
        if k == "m":
            select_llm.select_llm(session)
            continue
        elif k == "a":
            session.audio_mode.cycle()
            tt(f"Audio mode is now: {session.audio_mode.mode.upper()}.")
            suppress_menu = True
            continue
        elif k == "c":
            if last_image:
                tt("Showing last capture...")
                last_image.preview()
            else:
                tt("No last capture available (in the current session).", style="error")
            suppress_menu = True
            continue
        if k == key.SPACE:
            if not image:
                tt("Capturing image...")
                image = session.camera.capture()
                last_image = image  # Save the last capture for potential reuse
            if session.do_crop:
                tt("Cropping...")
                image = CroppedImage(image)
            image.preview()
            prompt = select_prompt.select_prompt(session)
        elif k == "p":
            prompt = select_prompt.select_prompt(session)
        elif k == key.ENTER:
            assert image is None
            prompt = get_textinput("Enter your prompt:")
        elif k == key.ESC:
            break
        else:
            tt("Unknown key. Please select a valid option.", style="error")
            suppress_menu = True
            continue

        if not prompt:
            tt("No prompt provided. Back to main menu.", style="error")
            continue

        # Now talk to the LLM(s):
        assert prompt is not None
        tp(request_panel(prompt))
        tt("Waiting for a response...")

        with background_animation(dot_animation):
            response = generate_completion(
                prompt,
                history=session.history,
                system_prompt=session.system_prompt,
                image=image,
                model=session.model_manager.current_model.api_name,
            )

        tp(response_panel(response))

        if session.audio_mode.should_ding():
            play_ding()

        if session.audio_mode.should_voice():
            tt("Generating voice output (in the background)...")
            speak_text(response)

        image = None
