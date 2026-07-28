from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowStep:
    """
    Represents a single workflow step.
    """

    action: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Workflow:
    """
    Represents a workflow definition.
    """

    name: str
    steps: list[WorkflowStep] = field(default_factory=list)
