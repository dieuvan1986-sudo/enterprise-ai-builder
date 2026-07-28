from actions.base import Action
from registry.base import Registry


class ActionRegistry(Registry[Action]):
    """
    Registry for workflow actions.
    """

    def register(self, action: Action) -> None:
        """
        Register an action instance.
        """
        super().register(
            action.name,
            action,
        )

    def get(self, name: str) -> Action:
        """
        Return an action by name.
        """
        return super().get(name)
