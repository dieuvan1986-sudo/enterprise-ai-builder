from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from applications.ai_money_factory.core.video_intelligence import (
    SceneDetectionEngine,
    SceneDetectionSettings,
)
from applications.ai_money_factory.core.video_intelligence.models import (
    DetectedScene,
    SourceVideo,
)


def main(
    argv: Sequence[str] | None = None,
) -> int:
    args = _parse_args(argv)
    source_path = Path(args.source_mp4)

    output_path = (
        Path(args.output_json)
        if args.output_json
        else source_path.parent / "scene_analysis.json"
    )

    engine = SceneDetectionEngine(
        SceneDetectionSettings(
            ffprobe_path=args.ffprobe_path,
            ffmpeg_path=args.ffmpeg_path,
            scene_threshold=args.scene_threshold,
            min_scene_duration_seconds=(
                args.min_scene_duration_seconds
            ),
            timeout_seconds=args.timeout_seconds,
        )
    )

    source_video, scenes = engine.detect(
        source_path
    )

    output_path.write_text(
        json.dumps(
            _analysis_payload(
                source_video,
                scenes,
            ),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    _print_timeline(scenes)

    return 0


def _parse_args(
    argv: Sequence[str] | None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze source MP4 scene boundaries "
            "for AI Money Factory."
        ),
    )

    parser.add_argument(
        "source_mp4",
        help="Path to the source MP4 file.",
    )

    parser.add_argument(
        "--output-json",
        help=(
            "Path for scene_analysis.json. "
            "Defaults next to the source MP4."
        ),
    )

    parser.add_argument(
        "--ffprobe-path",
        default="ffprobe",
    )

    parser.add_argument(
        "--ffmpeg-path",
        default="ffmpeg",
    )

    parser.add_argument(
        "--scene-threshold",
        type=float,
        default=0.35,
    )

    parser.add_argument(
        "--min-scene-duration-seconds",
        type=float,
        default=1.0,
    )

    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
    )

    return parser.parse_args(argv)


def _analysis_payload(
    source_video: SourceVideo,
    scenes: list[DetectedScene],
) -> dict[str, object]:
    return {
        "source": {
            **asdict(source_video),
            "path": str(source_video.path),
        },
        "scenes": [
            {
                **asdict(scene),
                "source_path": str(
                    scene.source_path
                ),
            }
            for scene in scenes
        ],
        "durations": {
            "source_seconds": (
                source_video.duration_seconds
            ),
            "detected_scene_seconds": [
                scene.duration_seconds
                for scene in scenes
            ],
            "total_detected_scene_seconds": round(
                sum(
                    scene.duration_seconds
                    for scene in scenes
                ),
                3,
            ),
        },
    }


def _print_timeline(
    scenes: list[DetectedScene],
) -> None:
    for scene in scenes:
        print(
            f"Scene {scene.scene_number}"
        )
        print(
            f"{_format_timestamp(scene.start_seconds)} "
            f"→ {_format_timestamp(scene.end_seconds)}"
        )
        print()


def _format_timestamp(
    seconds: float,
) -> str:
    milliseconds = round(
        seconds * 1000
    )
    minutes, remainder = divmod(
        milliseconds,
        60_000,
    )
    whole_seconds, milliseconds = divmod(
        remainder,
        1_000,
    )

    return (
        f"{minutes:02d}:"
        f"{whole_seconds:02d}."
        f"{milliseconds:03d}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
