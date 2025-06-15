from image import Image
from llm import generate_completion
from session import Session


chat_greeting = """\
============================================================
                 💬 STARTING CHAT SESSION 💬
============================================================
• Ask your follow-up questions.
• 'q/quit': Back to main loop
• 'capture': Take a new screenshot
------------------------------------------------------------
"""

chat_response_pattern = """\
Response:
============================================================
{response}
============================================================
"""


def chatloop(initial_image: Image, initial_prompt: str, session: Session) -> None:
    print(chat_greeting)

    print(f"Sent. Waiting for a response...")
    response = generate_completion(
        initial_prompt,
        image=initial_image,
        history=session.history,
        SYSTEM_PROMPT=session.system_prompt,
    )
    print(chat_response_pattern.format(response=response))
    while True:
        user_input = input("\n💬 Your message: ")

        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            print("Ending chat session.")
            break

        print(f"Sent. Waiting for a response...")
        response = generate_completion(
            user_input,
            history=session.history,
            SYSTEM_PROMPT=session.system_prompt,
        )
        print(chat_response_pattern.format(response=response))
