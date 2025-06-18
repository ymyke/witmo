from image import CroppedImage, BasicImage, Image
from session import Session
from readchar import readkey, key
from llm.completion import generate_completion
from llm.voice_output import speak_text
from tui.print_wrapped import pw
from tui.select_prompt import pick_prompt
from tui.select_llm import select_llm

menu = """\

Waiting for your command...
<space>  • capture a new image
<enter>  • enter prompt
'.'      • select LLM model
'!'      • toggle voice output
<escape> • quit
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
    - After the first use, initial_image is cleared to ensure normal behavior for the
      rest of the session.
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
            voice_state = "ON" if session.voice_output_enabled else "OFF"
            pw(
                f"[Voice: {voice_state}, LLM: {session.model_manager.current_model.shortname}]"
            )
            k = readkey()

        # Handle the different keys:
        if k == ".":
            select_llm(session)
            continue
        elif k == "!":
            session.voice_output_enabled = not session.voice_output_enabled
            pw(
                f"Voice output is now {'ON' if session.voice_output_enabled else 'OFF'}."
            )
            continue
        if k == key.SPACE:
            if not image:
                pw("Capturing image...")
                image = session.camera.capture()
            if session.do_crop:
                image = CroppedImage(image)
            image.preview()
            prompt = pick_prompt(session)
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
