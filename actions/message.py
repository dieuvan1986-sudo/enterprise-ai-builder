from rich import print

from actions.base import Action
from runtime.context import ActionContext


class MessageAction(Action):
    """
    Display a message to the console.
    """

    name = "message"

    def execute(
        self,
        step: dict,
        context: ActionContext,
    ) -> None:
        text = step.get("text", "")

        print(f"[bold blue]▶[/bold blue] {step['id']}")
        print(text)
        print("[green]✓ completed[/green]")
        print()
