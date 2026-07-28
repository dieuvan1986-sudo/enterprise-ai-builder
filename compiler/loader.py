from runtime.workflow import Workflow, WorkflowStep


def parse_workflow(data: dict) -> Workflow:
    """
    Parse a workflow dictionary into a Workflow model.
    """

    steps = []

    for item in data.get("steps", []):
        action = item.get("action")

        params = {
            key: value
            for key, value in item.items()
            if key != "action"
        }

        steps.append(
            WorkflowStep(
                action=action,
                params=params,
            )
        )

    return Workflow(
        name=data.get("name", "Unnamed Workflow"),
        steps=steps,
    )
