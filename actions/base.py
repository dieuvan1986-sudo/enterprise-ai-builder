from abc import ABC, abstractmethod

from runtime.context import ActionContext


class Action(ABC):
    """
    Base class for all Enterprise AI Builder actions.
    """

    #: Unique action name used inside workflow YAML.
    name: str = ""

    #: Human-readable description.
    description: str = ""

    #: Required parameters for this action.
    required_params: list[str] = []

    #: Optional parameters for this action.
    optional_params: list[str] = []

    @abstractmethod
    def execute(
        self,
        step: dict,
        context: ActionContext,
    ) -> None:
        """
        Execute one workflow step.
        """
        raise NotImplementedError
