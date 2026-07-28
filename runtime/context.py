from dataclasses import dataclass, field
from typing import Any

from runtime.workflow_state import WorkflowState


@dataclass
class ActionContext:
    """
    Shared execution context for a workflow run.
    """

    project: dict
    workflow: dict

    state: WorkflowState = field(default_factory=WorkflowState)

    variables: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def get_variable(
        self,
        key: str,
        default: Any = "",
    ) -> Any:
        return self.variables.get(key, default)

    def set_variable(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.variables[key] = value

    def update_variables(
        self,
        values: dict[str, Any],
    ) -> None:
        self.variables.update(values)
