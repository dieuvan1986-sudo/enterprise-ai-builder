"""
Enterprise AI Builder
Runtime - Execution Pipeline
Version: 0.1.0
"""

from runtime.workflow import WorkflowStep


class ExecutionPipeline:
    """
    Chịu trách nhiệm thực thi một Workflow Step.

    Hiện tại:
    - Gọi Action.execute()

    Trong các Sprint tiếp theo sẽ bổ sung:
    - Logging
    - Retry
    - Timeout
    - Metrics
    - Hook
    - Event
    - Plugin Interceptor
    """

    def __init__(self, registry):
        self.registry = registry

    def execute(self, step: WorkflowStep, context):
        """
        Thực thi một Workflow Step.
        """

        action_name = step.action

        action = self.registry.get(action_name)

        if action is None:
            raise ValueError(f"Action '{action_name}' is not registered.")

        action.execute(
            step=step,
            context=context,
        )
