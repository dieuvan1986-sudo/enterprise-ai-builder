from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from applications.ai_money_factory.core.video_factory import (
    VideoPackage,
    VideoScene,
)
from applications.ai_money_factory.core.voice_render import (
    OpenClawVoiceRenderer,
    VoiceRenderError,
)


def test_render_creates_wav_for_each_scene(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = _video_package()
    commands: list[list[str]] = []

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        Path(command[-1]).write_bytes(b"RIFF")

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    renderer = OpenClawVoiceRenderer(
        tmp_path,
        timeout=30,
        retry_delay_seconds=0,
    )

    result = renderer.render(package)

    assert result.title == package.title
    assert result.output_dir == tmp_path
    assert [scene.audio_path.name for scene in result.scenes] == [
        "scene_01_hook.wav",
        "scene_02_product_reveal.wav",
    ]
    assert all(scene.audio_path.is_file() for scene in result.scenes)
    assert commands == [
        [
            "openclaw",
            "infer",
            "tts",
            "convert",
            "--text",
            "Start here.",
            "--output",
            str(tmp_path / "scene_01_hook.wav"),
        ],
        [
            "openclaw",
            "infer",
            "tts",
            "convert",
            "--text",
            "Show the product.",
            "--output",
            str(tmp_path / "scene_02_product_reveal.wav"),
        ],
    ]


def test_render_retries_failed_scene(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = _video_package()
    calls = 0

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1

        if calls == 1:
            return subprocess.CompletedProcess(
                args=command,
                returncode=1,
                stdout="",
                stderr="temporary failure",
            )

        Path(command[-1]).write_bytes(b"RIFF")

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    renderer = OpenClawVoiceRenderer(
        tmp_path,
        max_attempts=2,
        retry_delay_seconds=0,
    )

    renderer.render(package)

    assert calls == 3


def test_render_raises_after_retries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = _video_package()

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr="permanent failure",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    renderer = OpenClawVoiceRenderer(
        tmp_path,
        max_attempts=2,
        retry_delay_seconds=0,
    )

    with pytest.raises(VoiceRenderError, match="permanent failure"):
        renderer.render(package)


def test_render_rejects_empty_narration(tmp_path: Path) -> None:
    package = VideoPackage(
        title="Test package",
        hook="Hook",
        scenes=[
            VideoScene(
                scene_number=1,
                duration_seconds=3,
                purpose="HOOK",
                narration=" ",
                visual_prompt="Visual",
            )
        ],
        cta="CTA",
        total_duration_seconds=3,
    )

    renderer = OpenClawVoiceRenderer(tmp_path)

    with pytest.raises(ValueError, match="narration cannot be empty"):
        renderer.render(package)


def _video_package() -> VideoPackage:
    return VideoPackage(
        title="Test package",
        hook="Start here.",
        scenes=[
            VideoScene(
                scene_number=1,
                duration_seconds=3,
                purpose="HOOK",
                narration="Start here.",
                visual_prompt="Visual one",
            ),
            VideoScene(
                scene_number=2,
                duration_seconds=5,
                purpose="PRODUCT_REVEAL",
                narration="Show the product.",
                visual_prompt="Visual two",
            ),
        ],
        cta="CTA",
        total_duration_seconds=8,
    )
