from __future__ import annotations

import json
import subprocess
from pathlib import Path

from applications.ai_money_factory.tools.analyze_source_video import main


def test_analyze_source_video_prints_timeline_and_writes_json(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    source_path = tmp_path / "source.mp4"
    output_path = tmp_path / "scene_analysis.json"
    source_path.write_bytes(b"video")

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
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
                                "r_frame_rate": "30/1",
                            }
                        ],
                        "format": {"duration": "5.0"},
                    }
                ),
                stderr="",
            )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr=(
                "[Parsed_showinfo] n:1 pts_time:2.153\n"
                "[Parsed_showinfo] n:2 pts_time:4.821\n"
            ),
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = main(
        [
            str(source_path),
            "--output-json",
            str(output_path),
            "--ffprobe-path",
            "ffprobe-test",
            "--ffmpeg-path",
            "ffmpeg-test",
            "--min-scene-duration-seconds",
            "0.1",
        ]
    )

    assert result == 0
    assert capsys.readouterr().out == (
        "Scene 1\n"
        "00:00.000 \u2192 00:02.153\n"
        "\n"
        "Scene 2\n"
        "00:02.153 \u2192 00:04.821\n"
        "\n"
        "Scene 3\n"
        "00:04.821 \u2192 00:05.000\n"
        "\n"
    )
    assert json.loads(output_path.read_text(encoding="utf-8")) == {
        "durations": {
            "detected_scene_seconds": [2.153, 2.668, 0.179],
            "source_seconds": 5.0,
            "total_detected_scene_seconds": 5.0,
        },
        "scenes": [
            {
                "duration_seconds": 2.153,
                "end_seconds": 2.153,
                "scene_number": 1,
                "source_path": str(source_path),
                "start_seconds": 0.0,
            },
            {
                "duration_seconds": 2.668,
                "end_seconds": 4.821,
                "scene_number": 2,
                "source_path": str(source_path),
                "start_seconds": 2.153,
            },
            {
                "duration_seconds": 0.179,
                "end_seconds": 5.0,
                "scene_number": 3,
                "source_path": str(source_path),
                "start_seconds": 4.821,
            },
        ],
        "source": {
            "duration_seconds": 5.0,
            "fps": 30.0,
            "height": 1920,
            "path": str(source_path),
            "width": 1080,
        },
    }
