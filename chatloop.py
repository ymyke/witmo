from image import Image
from llm import generate_completion
from session import Session


chat_greeting = """\
============================================================
                 💬 STARTING CHAT SESSION 💬
============================================================
• Ask your follow-up questions.
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
    initial_image: Image | None, initial_prompt: str, session: Session
) -> None:
    # TODO Needs to be able to handle initial_image == None
    print(chat_greeting)

    print(chat_request_pattern.format(request=initial_prompt))
    response = generate_completion(
        initial_prompt,
        image=initial_image,
        history=session.history,
        SYSTEM_PROMPT=session.system_prompt,
    )
    print(f"Waiting for a response...")
    print(chat_response_pattern.format(response=response))
    while True:
        user_input = input("\n💬 Your message: ")
        # TODO what about empty input?

        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            print("Ending chat session.")
            break

        print(chat_request_pattern.format(request=user_input))
        response = generate_completion(
            user_input,
            history=session.history,
            SYSTEM_PROMPT=session.system_prompt,
        )
        print(f"Waiting for a response...")
        print(chat_response_pattern.format(response=response))
