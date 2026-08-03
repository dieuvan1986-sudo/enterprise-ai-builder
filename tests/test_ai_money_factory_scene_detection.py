from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from applications.ai_money_factory.core.video_intelligence import (
    DetectedScene,
    SceneDetectionEngine,
    SceneDetectionError,
    SceneDetectionSettings,
    SourceVideo,
)


def test_detect_uses_ffprobe_and_ffmpeg_scene_boundaries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.mp4"
    source_path.write_bytes(b"video")
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

        if command[0] == "ffprobe-test":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout=json.dumps(
                    {
                        "streams": [
                            {
                                "width": 1080,
                                "height": 1920,
                                "r_frame_rate": "30000/1001",
                            }
                        ],
                        "format": {"duration": "10.0"},
                    }
                ),
                stderr="",
            )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr=(
                "[Parsed_showinfo] n:1 pts_time:1.2\n"
                "[Parsed_showinfo] n:2 pts_time:1.8\n"
                "[Parsed_showinfo] n:3 pts_time:4.5\n"
                "[Parsed_showinfo] n:4 pts_time:9.7\n"
            ),
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    source_video, scenes = SceneDetectionEngine(
        SceneDetectionSettings(
            ffprobe_path="ffprobe-test",
            ffmpeg_path="ffmpeg-test",
            scene_threshold=0.4,
            min_scene_duration_seconds=2,
            timeout_seconds=30,
        )
    ).detect(source_path)

    assert source_video == SourceVideo(
        path=source_path,
        duration_seconds=10,
        width=1080,
        height=1920,
        fps=29.97,
    )
    assert scenes == [
        DetectedScene(
            source_path=source_path,
            scene_number=1,
            start_seconds=0,
            end_seconds=4.5,
            duration_seconds=4.5,
        ),
        DetectedScene(
            source_path=source_path,
            scene_number=2,
            start_seconds=4.5,
            end_seconds=10,
            duration_seconds=5.5,
        ),
    ]
    assert commands[0] == [
        "ffprobe-test",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(source_path),
    ]
    assert commands[1] == [
        "ffmpeg-test",
        "-hide_banner",
        "-i",
        str(source_path),
        "-filter:v",
        "select='gt(scene,0.4)',showinfo",
        "-f",
        "null",
        "-",
    ]


def test_detect_returns_single_scene_when_no_boundaries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.mp4"
    source_path.write_bytes(b"video")

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        if command[0] == "ffprobe":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout=json.dumps(
                    {
                        "streams": [
                            {
                                "width": 720,
                                "height": 1280,
                                "r_frame_rate": "30/1",
                            }
                        ],
                        "format": {"duration": "6"},
                    }
                ),
                stderr="",
            )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    _, scenes = SceneDetectionEngine().detect(source_path)

    assert scenes == [
        DetectedScene(
            source_path=source_path,
            scene_number=1,
            start_seconds=0,
            end_seconds=6,
            duration_seconds=6,
        )
    ]


def test_detect_rejects_missing_source_video(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        SceneDetectionEngine().detect(tmp_path / "missing.mp4")


def test_detect_raises_when_ffprobe_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.mp4"
    source_path.write_bytes(b"video")

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
            stderr="bad probe",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(SceneDetectionError, match="bad probe"):
        SceneDetectionEngine().detect(source_path)


def test_settings_validate_scene_threshold() -> None:
    with pytest.raises(ValueError, match="scene_threshold"):
        SceneDetectionEngine(
            SceneDetectionSettings(scene_threshold=1.2)
        )
