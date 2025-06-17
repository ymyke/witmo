from image import CroppedImage, BasicImage, Image
from session import Session
from readchar import readkey, key
from print_utils import pw
from llm.completion import generate_completion
from llm.models import model_manager

menu = """\

Waiting for your command...
<space>  • capture a new image
<enter>  • enter prompt
'.'      • select LLM model
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
        prompt = None
        image: Image | None = None
        if initial_image:
            image = initial_image
            k = key.SPACE
        else:
            pw(menu)
            pw(f"[LLM: {model_manager.current_model.shortname}]")
            k = readkey()

        if k == ".":
            while True:
                pw(model_manager.as_menu())
                llmkey = readkey()
                if model_manager.has_key(llmkey):
                    model_manager.set_current_model_by_key(llmkey)
                    pw(f"LLM set to: {model_manager.current_model.name}")
                    break
                elif llmkey == key.ESC:
                    break
                else:
                    pw("Unknown key. Please select 3, 4, 5, or <escape>.")
            continue

        if k == key.SPACE:
            if not image:
                image = session.camera.capture()
            if session.do_crop:
                image = CroppedImage(image)
            image.preview()

            pw("\nPick your prompt:")
            for k, p in session.prompts.items():  # TODO use different k
                pw(f"'{k}' • {p['summary']} • [{p['prompt'][:60]}...]")
            pw("<enter> • enter your own prompt")

            while True:
                k = readkey()  # TODO use different k
                if k == key.ENTER:
                    prompt = input("\nEnter your prompt: ")
                    break
                elif k.lower() in session.prompts:
                    prompt = session.prompts[k]["prompt"]
                    pw(f"\nUsing prompt: {session.prompts[k]['summary']}")
                    break

                pw(f"Unknown key. Please select a valid option from the list.")

        elif k == key.ENTER:
            assert image is None
            prompt = input("\nEnter your prompt: ")

        elif k == key.ESC:
            break

        else:
            pw(f"Unknown key. Please select a valid option.")
            continue

        if prompt.strip().lower() in ["exit", "quit", "bye", "q"]:
            # Just in case the user wanted to quit after pressing enter
            continue

        assert prompt is not None
        pw(chat_request_pattern.format(request=prompt))
        response = generate_completion(
            prompt,
            history=session.history,
            SYSTEM_PROMPT=session.system_prompt,
            image=image,
            model=model_manager.current_model.api_name,
        )
        pw(f"Waiting for a response...")
        pw(chat_response_pattern.format(response=response))
        image = None
