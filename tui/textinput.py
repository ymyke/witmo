from textual.app import App, ComposeResult
from textual.widgets import TextArea, Button, Label
from textual.containers import Vertical, Horizontal
from textual import events
from textual.message import Message

# FIXME Make colors customizable as parameters


class SubmitMessage(Message):
    pass


class ExtendedTextArea(TextArea):
    def _on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+s":
            self.post_message(SubmitMessage())
            event.prevent_default()
            return


class TextInputApp(App):
    CSS = """
    Vertical {
      align: center middle;
      height: 100%;
    }

    #input-label {
      align: center middle;
      color: #3366FF;
      text-align: center;
      width: 100%;
      margin-bottom: 1;
    }

    #editor-container {
      align: center middle;
      height: auto;
    }

    TextArea {
      width: 60;
      height: 10;
      border: round #3366FF;    
      text-wrap: wrap;
    }

    Horizontal#buttons {
      align: center middle;
      height: auto;
      margin-right: 2;
    }

    Button#submit {
      background: #3366FF;
      color: white;
    }
    Button#cancel {
      background: #B3B3B3;
      color: black;
    }
    Button {
      width: auto;
      margin-top: 1;
      margin-right: 2;
    }
    """

    def __init__(self, label: str = "Input:", **kwargs):
        super().__init__(**kwargs)
        self.label_text = label

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.label_text, id="input-label")
            with Horizontal(id="editor-container"):
                self.textarea = ExtendedTextArea(id="editor")
                yield self.textarea

            with Horizontal(id="buttons"):
                yield Button("Submit\n(ctrl+s)", id="submit")
                yield Button("Cancel\n(ctrl+q)", id="cancel")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            await self._submit()
        elif event.button.id == "cancel":
            self.exit(None)

    async def on_submit_message(self, message: SubmitMessage) -> None:
        await self._submit()

    async def _submit(self) -> None:
        text = self.query_one(TextArea).text
        self.exit(text)


# Example usage:
if __name__ == "__main__":
    result = TextInputApp(label="Please enter your text below:").run()
    print("You entered:\n", result)
