import pytest

from runtime.workflow import Workflow, WorkflowStep
from validator.workflow_validator import WorkflowValidator


def test_valid_workflow():
    workflow = Workflow(
        name="demo",
        steps=[
            WorkflowStep(
                action="message",
                params={
                    "text": "Hello",
                },
            )
        ],
    )

    WorkflowValidator().validate(workflow)


def test_workflow_requires_name():
    workflow = Workflow(
        name="",
        steps=[
            WorkflowStep(
                action="message",
                params={},
            )
        ],
    )

    with pytest.raises(ValueError, match="Workflow name is required."):
        WorkflowValidator().validate(workflow)


def test_workflow_requires_steps():
    workflow = Workflow(
        name="demo",
        steps=[],
    )

    with pytest.raises(
        ValueError,
        match="Workflow must contain at least one step.",
    ):
        WorkflowValidator().validate(workflow)


def test_step_requires_action():
    workflow = Workflow(
        name="demo",
        steps=[
            WorkflowStep(
                action="",
                params={},
            )
        ],
    )

    with pytest.raises(
        ValueError,
        match="Step #1 is missing the 'action' field.",
    ):
        WorkflowValidator().validate(workflow)
