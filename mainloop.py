from image import CroppedImage, Image
from session import Session
from readchar import readkey, key
from chatloop import chatloop
from print_utils import pw

manual = """\
Waiting for your command...
<space>  • capture a new image
<enter>  • start chat w/o image
<escape> • quit
"""


def mainloop(session: Session, initial_image: Image | None = None) -> None:
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

        image = None
        prompt = None
        if initial_image:
            k = key.SPACE
        else:
            pw(manual)
            k = readkey()

        if k == key.SPACE:

            if initial_image:
                image = initial_image
            else:
                image = session.camera.capture()
                if session.do_crop:
                    image = CroppedImage(image)
            image.preview()

            pw("\nPick your prompt:")
            for k, p in session.prompts.items():
                pw(f"'{k}' • {p['summary']} • [{p['prompt'][:60]}...]")
            pw("<enter> • enter your own prompt")

            while True:
                k = readkey()
                if k == key.ENTER:
                    prompt = input("\nEnter your prompt: ")
                    break
                elif k.lower() in session.prompts:
                    prompt = session.prompts[k]["prompt"]
                    pw(f"\nUsing prompt: {session.prompts[k]['summary']}")
                    break

                pw(f"Unknown key. Please select a valid option from the list.")

        elif k == key.ENTER:
            image = None
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
        chatloop(session, prompt, image)
        initial_image = None
