import pytest

from runtime.pipeline import ExecutionPipeline
from runtime.workflow import WorkflowStep


class DummyAction:
    def __init__(self):
        self.executed = False

    def execute(self, step, context):
        self.executed = True


class DummyRegistry:
    def __init__(self):
        self._actions = {}

    def register(self, name, action):
        self._actions[name] = action

    def get(self, name):
        return self._actions.get(name)


def test_execute_action():
    """
    Pipeline phải gọi Action.execute().
    """

    registry = DummyRegistry()

    action = DummyAction()

    registry.register("dummy", action)

    pipeline = ExecutionPipeline(registry)

    step = WorkflowStep(
        action="dummy",
        params={
            "text": "Hello",
        },
    )

    context = object()

    pipeline.execute(step, context)

    assert action.executed is True


def test_action_not_found():
    """
    Pipeline phải báo lỗi nếu Action không tồn tại.
    """

    registry = DummyRegistry()

    pipeline = ExecutionPipeline(registry)

    step = WorkflowStep(
        action="unknown",
        params={},
    )

    with pytest.raises(ValueError):
        pipeline.execute(step, object())
