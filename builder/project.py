from pathlib import Path

import yaml


DEFAULT_PROJECT = """\
name: my-project
version: 0.1.0
description: Enterprise AI Builder project

workflow: workflows/main.yaml

llm:
  provider: openai
  model: gpt-5.5
"""


DEFAULT_WORKFLOW = """\
name: main

steps:
  - id: welcome
    action: message
    text: "Welcome to Enterprise AI Builder!"
"""


def create_project(path: str | Path) -> None:
    """
    Create a new Enterprise AI Builder project.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    project_file = path / "project.yaml"
    workflow_dir = path / "workflows"
    workflow_file = workflow_dir / "main.yaml"

    if not project_file.exists():
        project_file.write_text(DEFAULT_PROJECT, encoding="utf-8")

    workflow_dir.mkdir(exist_ok=True)

    if not workflow_file.exists():
        workflow_file.write_text(DEFAULT_WORKFLOW, encoding="utf-8")


def load_project(path: str | Path = ".") -> dict:
    """
    Load project.yaml from the specified directory.
    """
    path = Path(path)
    project_file = path / "project.yaml"

    if not project_file.exists():
        raise FileNotFoundError(
            f"project.yaml not found: {project_file.resolve()}"
        )

    with project_file.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_workflow(path: str | Path) -> dict:
    """
    Load a workflow YAML file.
    """
    workflow_file = Path(path)

    if not workflow_file.exists():
        raise FileNotFoundError(
            f"Workflow not found: {workflow_file.resolve()}"
        )

    with workflow_file.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
