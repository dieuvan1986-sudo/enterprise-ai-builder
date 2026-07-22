from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionContext:
    """
    Shared execution context for a workflow run.
    """

    project: dict
    workflow: dict

    variables: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)
