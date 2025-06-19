from image import CroppedImage, BasicImage, Image
from session import Session
from readchar import readkey, key
from llm.completion import generate_completion
from llm.voice_output import speak_text
from tui.print_wrapped import pw
from tui import select_prompt
from tui import select_llm

menu = """\

Waiting for your command...
 space = capture a new image
 enter = enter free-text prompt
     ? = show all preconfigured prompts
     ^ = pick preconfigured prompt and send it
     . = select LLM model
     ! = toggle voice output
   esc = quit
"""

chat_request_pattern = """\
Request:
------------------------------------------------------------
{request}
------------------------------------------------------------
"""

chat_response_pattern = """\
Response:
============================================================
{response}
============================================================
"""


def mainloop(session: Session, initial_image: BasicImage | None = None) -> None:
    """Main interactive loop for the application.

    Behavior:
    - If initial_image is provided, the loop will immediately use it as the image for
      the first prompt selection, skipping the manual and image capture step.
    - Otherwise, the user is prompted to capture a new image, start a chat without an
      image, or quit.
    """

    while True:

        # Setup, show menu, handle special case where initial_image is provided:
        prompt = None
        image: Image | None = None
        if initial_image:
            image = initial_image
            k = key.SPACE
        else:
            pw(menu)
            pw(
                f"[Voice: {'ON' if session.voice_output_enabled else 'OFF'} • "
                f"LLM: {session.model_manager.current_model.shortname} • "
                f"Crop: {'ON' if session.do_crop else 'OFF'}]\n"
            )
            k = readkey()

        # Handle the different keys:
        if k == ".":
            select_llm.select_llm(session)
            continue
        elif k == "!":
            session.voice_output_enabled = not session.voice_output_enabled
            pw(
                f"Voice output is now {'ON' if session.voice_output_enabled else 'OFF'}."
            )
            continue
        elif k == "?":
            select_prompt.show_full_menu(session)
            continue
        if k == key.SPACE:
            if not image:
                pw("Capturing image...")
                image = session.camera.capture()
            if session.do_crop:
                image = CroppedImage(image)
            image.preview()
            prompt = select_prompt.select_prompt(session)
        elif k == "^":
            prompt = select_prompt.select_prompt(session)
        elif k == key.ENTER:
            assert image is None
            prompt = input("\nEnter your prompt: ")
        elif k == key.ESC:
            break
        else:
            pw(f"Unknown key. Please select a valid option.")
            continue

        # Let the user quit after pressing enter:
        if prompt.lower() in ["quit", "q", "exit", "cancel"]:
            continue

        # Now talk to the LLM(s):
        assert prompt is not None
        pw(chat_request_pattern.format(request=prompt))
        response = generate_completion(
            prompt,
            history=session.history,
            system_prompt=session.system_prompt,
            image=image,
            model=session.model_manager.current_model.api_name,
        )
        pw(f"Waiting for a response...")
        pw(chat_response_pattern.format(response=response))
        if session.voice_output_enabled:
            speak_text(response)
        image = None
