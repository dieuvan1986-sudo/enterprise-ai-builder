from abc import ABC, abstractmethod

from runtime.context import ActionContext


class Action(ABC):
    """
    Base class for all Enterprise AI Builder actions.
    """

    #: Unique action name used inside workflow YAML.
    name: str = ""

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
