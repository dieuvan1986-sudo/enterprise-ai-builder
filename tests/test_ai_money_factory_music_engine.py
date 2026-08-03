from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from applications.ai_money_factory.core.music_engine import (
    MusicEngine,
    MusicEngineError,
    MusicRenderConfig,
)


def test_render_loops_music_to_target_duration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.mp3"
    source_path.write_bytes(b"audio")
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

    result = MusicEngine().render(
        MusicRenderConfig(
            source_path=source_path,
            output_dir=tmp_path / "music",
            target_duration_seconds=8.5,
            title="Promo Sauce",
            ffmpeg_path="custom-ffmpeg",
        )
    )

    assert result.title == "Promo Sauce"
    assert result.source_path == source_path
    assert result.audio_path == tmp_path / "music" / "promo_sauce_music.wav"
    assert result.audio_path.is_file()
    assert result.duration_seconds == 8.5
    assert result.fit_mode == "loop"
    assert commands == [
        [
            "custom-ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(source_path),
            "-t",
            "8.5",
            "-vn",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-af",
            "volume=0.18",
            "-c:a",
            "pcm_s16le",
            str(tmp_path / "music" / "promo_sauce_music.wav"),
        ]
    ]


def test_render_trims_music_without_looping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.wav"
    source_path.write_bytes(b"audio")
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

    result = MusicEngine().render(
        MusicRenderConfig(
            source_path=source_path,
            output_dir=tmp_path,
            output_filename="bed.wav",
            target_duration_seconds=3,
            fit_mode="trim",
            sample_rate_hz=44_100,
            channels=1,
            volume=0.25,
        )
    )

    assert "-stream_loop" not in commands[0]
    assert commands[0] == [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-t",
        "3",
        "-vn",
        "-ac",
        "1",
        "-ar",
        "44100",
        "-af",
        "volume=0.25",
        "-c:a",
        "pcm_s16le",
        str(tmp_path / "bed.wav"),
    ]
    assert result.audio_path == tmp_path / "bed.wav"


def test_render_rejects_missing_music_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        MusicEngine().render(
            MusicRenderConfig(
                source_path=tmp_path / "missing.mp3",
                output_dir=tmp_path,
                target_duration_seconds=5,
            )
        )


def test_render_raises_when_ffmpeg_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.mp3"
    source_path.write_bytes(b"audio")

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
            stderr="bad audio",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MusicEngineError, match="bad audio"):
        MusicEngine().render(
            MusicRenderConfig(
                source_path=source_path,
                output_dir=tmp_path,
                target_duration_seconds=5,
            )
        )
