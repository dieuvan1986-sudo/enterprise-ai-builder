from actions.base import Action


class ActionRegistry:
    """
    Registry for workflow actions.
    """

    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, action: Action) -> None:
        """
        Register an action instance.
        """
        self._actions[action.name] = action

    def get(self, name: str) -> Action:
        """
        Return an action by name.
        """
        if name not in self._actions:
            raise ValueError(f"Unknown action: {name}")

        return self._actions[name]

    def names(self) -> list[str]:
        """
        Return all registered action names.
        """
        return sorted(self._actions.keys())
