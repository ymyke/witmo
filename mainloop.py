from image import Image
from session import Session
from chatloop import chatloop


def mainloop(session: Session, image: Image | None = None) -> None:
    while True:
        if not image:
            key = input("\nPress Enter to capture a new image or type 'q' to quit: ")
            # TODO switch to non-blocking input
            if key == "q":
                break
            image = session.camera.capture()

        assert image, "Image should not be None at this point."
        image.preview()

        # TODO do proper prompt selection here
        prompt = f"{session.game_name}: Describe what we see here and help me understand what's happening. Do not just read out what is there. I can read the screen myself. Focus on giving me insights, help me understand, provide truly useful information."
        chatloop(image, prompt, session)

        image = None
