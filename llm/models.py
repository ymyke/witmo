from dataclasses import dataclass


@dataclass
class Model:
    shortname: str
    name: str
    api_name: str


class ModelManager:
    def __init__(self):
        self._models: dict[str, Model] = {
            "3": Model(shortname="o3", name="OpenAI o3", api_name="o3"),
            "4": Model(shortname="4o", name="OpenAI 4o", api_name="gpt-4o"),
            "5": Model(
                shortname="4.5", name="OpenAI 4.5", api_name="gpt-4.5-preview"
            ),
        }
        self._current_key = "3"

    @property
    def current_model(self) -> Model:
        return self._models[self._current_key]

    def set_current_model_by_key(self, key: str) -> None:
        if key in self._models:
            self._current_key = key
        else:
            raise ValueError(f"Unknown model key: {key}")
        print(f"LLM set to: {self.current_model.name} ({self.current_model.shortname})")

    def has_key(self, key) -> bool:
        return key in self._models

    def as_menu(self) -> str:   # TODO maybe to mainloop?
        menu = "\nSelect LLM model:\n"
        for key, model in self._models.items():
            appendix = " (CURRENT)" if key == self._current_key else ""
            menu += f"{key} • {model.name}{appendix}\n"
        return menu


# Singleton instance:
model_manager = ModelManager()
