
import pytest

from builder.project import create_project


def test_create_project(tmp_path, monkeypatch):
    """A new project should be created with the expected structure."""

    monkeypatch.chdir(tmp_path)

    project_dir = create_project("demo")

    assert project_dir.exists()
    assert project_dir.name == "demo"

    expected_directories = [
        "agents",
        "workflows",
        "plugins",
        "prompts",
        "knowledge",
        "output",
    ]

    for directory in expected_directories:
        assert (project_dir / directory).is_dir()

    assert (project_dir / "project.yaml").is_file()
    assert (project_dir / "README.md").is_file()


def test_create_project_existing_directory(tmp_path, monkeypatch):
    """Creating an existing project should raise FileExistsError."""

    monkeypatch.chdir(tmp_path)

    create_project("demo")

    with pytest.raises(FileExistsError):
        create_project("demo")
