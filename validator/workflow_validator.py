from actions.registry import ActionRegistry
from runtime.workflow import Workflow


class WorkflowValidator:
    """
    Validate a workflow before execution.
    """

    def __init__(
        self,
        registry: ActionRegistry | None = None,
    ) -> None:
        """
        Initialize the workflow validator.

        The registry is optional for now and will be used in future
        validation stages (unknown actions, required parameters, etc.).
        """
        self.registry = registry

    def validate(self, workflow: Workflow) -> None:
        """
        Raise ValueError if the workflow is invalid.
        """

        if not workflow.name:
            raise ValueError("Workflow name is required.")

        if not workflow.steps:
            raise ValueError("Workflow must contain at least one step.")

        for index, step in enumerate(workflow.steps, start=1):
            if not step.action:
                raise ValueError(
                    f"Step #{index} is missing the 'action' field."
                )
