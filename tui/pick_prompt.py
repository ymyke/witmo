
from readchar import readkey, key
from tui.print_wrapped import pw
from session import Session


def pick_prompt(session: Session) -> str:
    pw("\nPick your prompt:") # TODO only do this once? no need to have this in session? (then, get rid of session param?)
    for k, p in session.prompts.items():  
        pw(f"'{k}' • {p['summary']} • [{p['prompt'][:60]}...]")
    pw("<enter> • enter your own prompt")

    while True:
        k = readkey()  
        if k == key.ENTER:
            while True:
                prompt = input("\nEnter your prompt: ").strip()
                if prompt:
                    break
                pw("Please enter a prompt. Or enter 'q' to cancel.")
            break
        elif k.lower() in session.prompts:
            prompt = session.prompts[k]["prompt"]
            pw(f"\nUsing prompt: {session.prompts[k]['summary']}")
            break
        pw(f"Unknown key. Please select a valid option from the list.")

    return prompt
