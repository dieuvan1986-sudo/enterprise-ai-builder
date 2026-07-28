from actions.message import MessageAction
from actions.registry import ActionRegistry


def create_action_registry() -> ActionRegistry:
    """
    Create and initialize the default ActionRegistry.

    This is the single bootstrap point responsible for registering all
    built-in actions. Runtime, Validator, CLI and future PluginManager
    should obtain their registry from here.
    """

    registry = ActionRegistry()

    # Built-in actions
    registry.register(MessageAction())

    return registry
