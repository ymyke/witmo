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
            "5": Model(shortname="4.5", name="OpenAI 4.5", api_name="gpt-4.5-preview"),
        }
        self._current_key = self._models.keys().__iter__().__next__()

    @property
    def current_model(self) -> Model:
        return self._models[self._current_key]

    def set_current_model_by_key(self, key: str) -> None:
        if key in self._models:
            self._current_key = key
        else:
            raise ValueError(f"Unknown model key: {key}")

    def has_key(self, key) -> bool:
        return key in self._models
