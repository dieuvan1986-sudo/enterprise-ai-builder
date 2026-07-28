from compiler.loader import parse_workflow
from runtime.workflow import Workflow, WorkflowStep


def test_parse_workflow():
    """
    Parse workflow dictionary into Workflow model.
    """

    data = {
        "name": "Example",
        "steps": [
            {
                "action": "message",
                "text": "Hello",
            }
        ],
    }

    workflow = parse_workflow(data)

    assert isinstance(workflow, Workflow)
    assert workflow.name == "Example"

    assert len(workflow.steps) == 1

    step = workflow.steps[0]

    assert isinstance(step, WorkflowStep)
    assert step.action == "message"

    assert step.params == {
        "text": "Hello",
    }


def test_parse_empty_workflow():
    """
    Empty workflow should contain no steps.
    """

    workflow = parse_workflow({})

    assert workflow.name == "Unnamed Workflow"
    assert workflow.steps == []
