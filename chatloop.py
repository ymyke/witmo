from image import Image
from llm import generate_completion
from session import Session
from print_utils import pw


chat_greeting = """\
============================================================
                 💬 STARTING CHAT SESSION 💬
============================================================
• Ask your follow-up questions.
• 'c/cap/capture': Take a new screenshot
• 'q/quit': Back to main loop
------------------------------------------------------------
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


def chatloop(
    session: Session, initial_prompt: str, initial_image: Image | None
) -> None:

    pw(chat_greeting)

    image = initial_image
    user_input = initial_prompt
    while True:

        pw(chat_request_pattern.format(request=user_input))
        response = generate_completion(
            user_input,
            history=session.history,
            SYSTEM_PROMPT=session.system_prompt,
            image=image,
        )
        pw(f"Waiting for a response...")
        pw(chat_response_pattern.format(response=response))

        image = None  # Clear image so we don't constantly re-send it

        prompt_prompt = "\n💬 Your follow-on request: "
        while True:
            user_input = input(prompt_prompt)
            user_input = user_input.strip()

            if user_input.lower() in ["capture", "cap", "c"]:
                image = session.camera.capture()
                image.preview()
                prompt_prompt = "\n💬 Your request with that new image: "
                continue  # Also get the prompt for that image

            if not user_input:  # Ensure we don't send empty requests
                continue

            break

        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            pw("Ending chat session.")
            break
