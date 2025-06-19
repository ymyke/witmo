from readchar import readkey, key
from tui.print_wrapped import pw
from session import Session


def show_full_menu(session: Session) -> None:
    pw("\nAll preconfigured prompts in full:\n\n")
    for k, p in session.prompts.items():
        pw(f"{k} = {p['summary']}\n{p['prompt']}\n{'-'*60}")
    pw()


def show_short_menu(session: Session) -> None:
    pw("\nPick your prompt:")
    for k, p in session.prompts.items():
        pw(f"{k} = {p['summary']}   [{p['prompt'][:60]}...]")
    pw("enter = enter your own prompt\n\n")


def select_prompt(session: Session) -> str:
    show_short_menu(session)
    while True:
        k = readkey()
        if k == key.ENTER:
            while True:
                prompt = input("\nEnter your prompt: ").strip()
                pw()
                if prompt:
                    break
                pw("Please enter a prompt. Or enter 'q' to cancel.\n\n")
            break
        elif k.lower() in session.prompts:
            prompt = session.prompts[k]["prompt"]
            pw(f"\nUsing prompt: {session.prompts[k]['summary']}\n\n")
            break
        pw(f"Unknown key. Please select a valid option from the list.")

    return prompt
