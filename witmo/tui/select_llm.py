from readchar import readkey, key
from witmo.session import Session
from witmo.tui.io import tt, menu_panel


def show_menu(session):
    m = []
    for key, model in session.model_manager._models.items():
        appendix = " (CURRENT)" if key == session.model_manager._current_key else ""
        m.append((key, f"{model.name}{appendix}"))
    tt(menu_panel("Select LLM", m, "low"))


def select_llm(session: Session) -> None:
    while True:
        show_menu(session)
        k = readkey()
        if session.model_manager.has_key(k):
            session.model_manager.set_current_model_by_key(k)
            tt(f"LLM set to: {session.model_manager.current_model.name}")
            break
        elif k == key.ESC:
            break
        else:
            tt("Unknown key. Please select 3, 4, 5, or <escape>.", style="error")
