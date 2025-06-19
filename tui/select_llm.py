from readchar import readkey, key
from tui.print_wrapped import pw
from session import Session


def show_menu(session):
    menu = "\nSelect LLM model:\n"
    for key, model in session.model_manager._models.items():
        appendix = " (CURRENT)" if key == session.model_manager._current_key else ""
        menu += f"{key} = {model.name}{appendix}\n"
    return menu


def select_llm(session: Session) -> None:
    while True:
        pw(show_menu(session))
        k = readkey()
        if session.model_manager.has_key(k):
            session.model_manager.set_current_model_by_key(k)
            pw(f"LLM set to: {session.model_manager.current_model.name}")
            break
        elif k == key.ESC:
            break
        else:
            pw("Unknown key. Please select 3, 4, 5, or <escape>.")
