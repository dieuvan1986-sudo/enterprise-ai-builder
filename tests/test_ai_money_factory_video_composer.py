from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from applications.ai_money_factory.core.content_models import SubtitleCue, SubtitleTrack
from applications.ai_money_factory.core.music_engine import MusicTrack
from applications.ai_money_factory.core.video_composer import (
    VideoComposer,
    VideoComposerError,
    VideoCompositionRequest,
    VideoRenderConfig,
    VisualAsset,
)
from applications.ai_money_factory.core.voice_render import (
    VoiceRenderResult,
    VoiceSceneRender,
)


def test_compose_renders_and_verifies_vertical_mp4(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    visual_path = _write_file(tmp_path / "visual.png")
    voice_path = _write_file(tmp_path / "voice.wav")
    music_path = _write_file(tmp_path / "music.wav")
    output_path = tmp_path / "final.mp4"
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

        if command[0] == "ffmpeg-test":
            output_path.write_bytes(b"mp4")

            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="",
                stderr="",
            )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(
                {
                    "streams": [
                        {
                            "width": 1080,
                            "height": 1920,
                            "codec_name": "h264",
                        }
                    ],
                    "format": {"duration": "5.0"},
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = VideoComposer().compose(
        VideoCompositionRequest(
            title="Final short",
            visual_assets=[
                VisualAsset(
                    scene_number=1,
                    path=visual_path,
                    duration_seconds=5,
                )
            ],
            voice_track=VoiceRenderResult(
                title="Voice",
                output_dir=tmp_path,
                scenes=[
                    VoiceSceneRender(
                        scene_number=1,
                        purpose="HOOK",
                        narration="Start here.",
                        audio_path=voice_path,
                    )
                ],
            ),
            subtitles=SubtitleTrack(
                title="Subtitles",
                total_duration_seconds=5,
                cues=[
                    SubtitleCue(
                        scene_number=1,
                        cue_number=1,
                        start_seconds=0,
                        end_seconds=5,
                        text="Start here.",
                    )
                ],
            ),
            music_track=MusicTrack(
                title="Music",
                source_path=music_path,
                audio_path=music_path,
                duration_seconds=5,
                fit_mode="loop",
            ),
            output_path=output_path,
            config=VideoRenderConfig(
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
            ),
        )
    )

    ffmpeg_command = commands[0]
    ffprobe_command = commands[1]

    assert result.output_path == output_path
    assert result.duration_seconds == 5
    assert result.width == 1080
    assert result.height == 1920
    assert result.fps == 30
    assert result.video_codec == "libx264"
    assert result.audio_codec == "aac"
    assert result.has_voice is True
    assert result.has_music is True
    assert result.has_subtitles is True
    assert output_path.is_file()
    assert ffmpeg_command[0] == "ffmpeg-test"
    assert "-filter_complex" in ffmpeg_command
    assert "scale=1080:1920" in ffmpeg_command[ffmpeg_command.index("-filter_complex") + 1]
    assert "subtitles=" in ffmpeg_command[ffmpeg_command.index("-filter_complex") + 1]
    assert "amix=inputs=2" in ffmpeg_command[ffmpeg_command.index("-filter_complex") + 1]
    assert "-c:v" in ffmpeg_command
    assert "libx264" in ffmpeg_command
    assert "yuv420p" in ffmpeg_command
    assert str(output_path) == ffmpeg_command[-1]
    assert ffprobe_command[0] == "ffprobe-test"
    assert str(output_path) == ffprobe_command[-1]


def test_compose_fails_fast_when_visual_is_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Visual asset"):
        VideoComposer().compose(
            VideoCompositionRequest(
                title="Missing visual",
                visual_assets=[
                    VisualAsset(
                        scene_number=1,
                        path=tmp_path / "missing.png",
                        duration_seconds=5,
                    )
                ],
                voice_track=None,
                subtitles=None,
                music_track=None,
                output_path=tmp_path / "final.mp4",
            )
        )


def test_compose_raises_when_ffmpeg_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    visual_path = _write_file(tmp_path / "visual.png")

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
            stderr="bad render",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(VideoComposerError, match="bad render"):
        VideoComposer().compose(
            VideoCompositionRequest(
                title="Bad render",
                visual_assets=[
                    VisualAsset(
                        scene_number=1,
                        path=visual_path,
                        duration_seconds=5,
                    )
                ],
                voice_track=None,
                subtitles=None,
                music_track=None,
                output_path=tmp_path / "final.mp4",
            )
        )


def test_compose_raises_when_ffprobe_rejects_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    visual_path = _write_file(tmp_path / "visual.png")
    output_path = tmp_path / "final.mp4"
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
            output_path.write_bytes(b"mp4")

            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="",
                stderr="",
            )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(
                {
                    "streams": [{"width": 720, "height": 1280}],
                    "format": {"duration": "5.0"},
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(VideoComposerError, match="width"):
        VideoComposer().compose(
            VideoCompositionRequest(
                title="Bad probe",
                visual_assets=[
                    VisualAsset(
                        scene_number=1,
                        path=visual_path,
                        duration_seconds=5,
                    )
                ],
                voice_track=None,
                subtitles=None,
                music_track=None,
                output_path=output_path,
            )
        )


def _write_file(path: Path) -> Path:
    path.write_bytes(b"asset")

    return path
