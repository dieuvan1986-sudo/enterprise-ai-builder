from rich import print

from actions.base import Action
from runtime.context import ActionContext
from runtime.template import render
from runtime.workflow import WorkflowStep


class MessageAction(Action):
    """
    Display a message to the console.
    """

    name = "message"

    description = "Display a message to the console."

    required_params = [
        "text",
    ]

    optional_params = [
        "id",
    ]

    def execute(
        self,
        step: WorkflowStep,
        context: ActionContext,
    ) -> None:

        executed_steps = context.state.get("executed_steps", [])

        step_id = step.params.get("id", step.action)

        executed_steps.append(step_id)

        context.state.set(
            "executed_steps",
            executed_steps,
        )

        text = render(
            step.params.get("text", ""),
            context,
        )

        print(f"[bold blue]▶[/bold blue] {step_id}")
        print(text)
        print("[green]✓ completed[/green]")
        print()
