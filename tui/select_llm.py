from readchar import readkey, key
from tui.print_wrapped import pw
from session import Session


def select_llm(session: Session) -> None:
    while True:
        pw(session.model_manager.as_menu())  # TODO
        k = readkey()
        if session.model_manager.has_key(k):
            session.model_manager.set_current_model_by_key(k)
            pw(f"LLM set to: {session.model_manager.current_model.name}")
            break
        elif k == key.ESC:
            break
        else:
            pw("Unknown key. Please select 3, 4, 5, or <escape>.")
