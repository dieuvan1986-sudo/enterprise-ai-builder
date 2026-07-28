from rich import print

from actions.base import Action
from actions.bootstrap import create_action_registry
from registry.base import Registry
from runtime.context import ActionContext
from runtime.lifecycle import RuntimePhase
from runtime.pipeline import ExecutionPipeline
from runtime.workflow import Workflow
from runtime.workflow_state import WorkflowState


class RuntimeEngine:
    """
    Enterprise AI Builder Runtime Engine.

    The RuntimeEngine coordinates workflow execution according to the
    Runtime Lifecycle defined by RFC-0005.
    """

    def __init__(
        self,
        project: dict,
        registry: Registry[Action] | None = None,
    ) -> None:
        self.project = project

        # Current runtime lifecycle phase.
        self.phase: RuntimePhase | None = None

        # Backward-compatible default.
        if registry is None:
            registry = create_action_registry()

        self.registry = registry
        self.pipeline = ExecutionPipeline(self.registry)

    def _set_phase(self, phase: RuntimePhase) -> None:
        """
        Update the current runtime lifecycle phase.

        Future versions may publish events, collect metrics,
        emit traces and notify plugins from this method.
        """
        self.phase = phase

    def run(self, workflow: Workflow) -> None:
        self._set_phase(RuntimePhase.INITIALIZE)

        state = WorkflowState()

        self._set_phase(RuntimePhase.LOAD_SERVICES)

        self._set_phase(RuntimePhase.LOAD_WORKFLOW)

        self._set_phase(RuntimePhase.BUILD_EXECUTION_CONTEXT)

        context = ActionContext(
            project=self.project,
            workflow=workflow,
            state=state,
            variables={
                "user": "Van",
                "company": "Enterprise AI Builder",
            },
        )

        print(f"[bold cyan]Running workflow:[/bold cyan] {workflow.name}")
        print()

        if not workflow.steps:
            self._set_phase(RuntimePhase.SHUTDOWN)
            print("[yellow]No steps found.[/yellow]")
            return

        self._set_phase(RuntimePhase.EXECUTE_WORKFLOW)

        for step in workflow.steps:
            self.pipeline.execute(
                step=step,
                context=context,
            )

        self._set_phase(RuntimePhase.PUBLISH_EVENTS)

        print("[green]Workflow finished successfully.[/green]")
        print()
        print("[bold magenta]Workflow State[/bold magenta]")
        print(context.state.to_dict())

        self._set_phase(RuntimePhase.CLEANUP)

        self._set_phase(RuntimePhase.SHUTDOWN)
