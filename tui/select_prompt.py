from readchar import readkey, key
from session import Session
from tui.io import tt, menu_panel, get_textinput


def show_full_menu(session: Session) -> None:
    m = []
    for k, p in session.prompts.items():
        m.append((k, p["summary"]))
        m.append(("", p["prompt"]))
    tt(menu_panel("Preconfigured prompts", m, "low"))


def show_short_menu(session: Session) -> None:
    m = []
    for k, p in session.prompts.items():
        m.append((k, p["summary"], p["prompt"][:60] + "..."))
    m.append(("enter", "enter your own prompt"))
    tt(menu_panel("Pick a prompt", m, "med"))


def select_prompt(session: Session) -> str:
    tt()
    show_short_menu(session)
    while True:
        k = readkey()
        if k == key.ENTER:
            prompt = get_textinput("Enter your prompt:")
            break
        elif k.lower() in session.prompts:
            prompt = session.prompts[k]["prompt"]
            tt(f"\nUsing prompt: {session.prompts[k]['summary']}\n\n")
            break
        tt(f"Unknown key. Please select a valid option from the list.", style="error")

    return prompt
