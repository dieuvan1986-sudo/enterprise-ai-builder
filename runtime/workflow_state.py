from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowState:
    """
    Stores the mutable state of a workflow while it is running.
    """

    values: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.values[key] = value

    def contains(self, key: str) -> bool:
        return key in self.values

    def to_dict(self) -> dict[str, Any]:
        return dict(self.values)
