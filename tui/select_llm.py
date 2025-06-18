from readchar import readkey, key
from tui.print_wrapped import pw
from llm.models import model_manager


def select_llm() -> None:
    while True:
        pw(model_manager.as_menu())  # TODO
        k = readkey()
        if model_manager.has_key(k):
            model_manager.set_current_model_by_key(k)
            pw(f"LLM set to: {model_manager.current_model.name}")
            break
        elif k == key.ESC:
            break
        else:
            pw("Unknown key. Please select 3, 4, 5, or <escape>.")
