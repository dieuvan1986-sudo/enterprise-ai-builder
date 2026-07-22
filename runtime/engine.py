from rich import print

from actions.message import MessageAction
from actions.registry import ActionRegistry
from runtime.context import ActionContext


class RuntimeEngine:
    """
    Enterprise AI Builder Runtime Engine.
    """

    def __init__(self, project: dict) -> None:
        self.project = project

        self.registry = ActionRegistry()

        # Register built-in actions
        self.registry.register(MessageAction())

    def run(self, workflow: dict) -> None:
        context = ActionContext(
            project=self.project,
            workflow=workflow,
        )

        workflow_name = workflow.get("name", "Unnamed Workflow")
        steps = workflow.get("steps", [])

        print(f"[bold cyan]Running workflow:[/bold cyan] {workflow_name}")
        print()

        if not steps:
            print("[yellow]No steps found.[/yellow]")
            return

        for step in steps:
            action_name = step.get("action")

            action = self.registry.get(action_name)

            action.execute(
                step=step,
                context=context,
            )

        print("[green]Workflow finished successfully.[/green]")
