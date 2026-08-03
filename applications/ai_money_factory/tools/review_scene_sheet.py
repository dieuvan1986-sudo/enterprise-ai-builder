from __future__ import annotations

import argparse
import html
import json
import math
import struct
from pathlib import Path
from typing import Sequence

THUMBNAIL_EXTENSIONS = (".jpg", ".jpeg", ".png")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    analysis_path = Path(args.scene_analysis_json)
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else analysis_path.parent
    )
    contact_sheet_path = (
        output_dir / "scene_review_contact_sheet.svg"
    )
    template_path = (
        output_dir / "scene_review_template.json"
    )

    analysis = _read_analysis(analysis_path)
    scenes = _analysis_scenes(analysis)
    thumbnails = [
        _thumbnail_for_scene(
            scene=scene,
            analysis_path=analysis_path,
            thumbnail_dir=(
                Path(args.thumbnail_dir)
                if args.thumbnail_dir
                else None
            ),
        )
        for scene in scenes
    ]

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    contact_sheet_path.write_text(
        _contact_sheet_svg(thumbnails),
        encoding="utf-8",
    )

    template_exists = template_path.exists()

    if args.force or not template_exists:
        template_path.write_text(
            _template_json(scenes),
            encoding="utf-8",
        )

    print(f"Wrote {contact_sheet_path}")

    if args.force or not template_exists:
        print(f"Wrote {template_path}")
    else:
        print(
            "Scene review template already exists: "
            f"{template_path}"
        )
        print("Use --force to overwrite.")

    return 0


def _parse_args(
    argv: Sequence[str] | None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a deterministic scene review sheet."
        ),
    )

    parser.add_argument(
        "scene_analysis_json",
        help=(
            "Path to scene_analysis.json "
            "from analyze_source_video.py."
        ),
    )

    parser.add_argument(
        "--thumbnail-dir",
        help=(
            "Directory containing scene thumbnails. "
            "Defaults to thumbnails/ next to "
            "scene_analysis.json."
        ),
    )

    parser.add_argument(
        "--output-dir",
        help=(
            "Directory for "
            "scene_review_contact_sheet.svg and "
            "scene_review_template.json."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite an existing "
            "scene_review_template.json."
        ),
    )

    return parser.parse_args(argv)


def _read_analysis(
    analysis_path: Path,
) -> dict[str, object]:
    if not analysis_path.is_file():
        raise FileNotFoundError(
            "Scene analysis file does not exist: "
            f"{analysis_path}"
        )

    return json.loads(
        analysis_path.read_text(
            encoding="utf-8",
        )
    )


def _analysis_scenes(
    analysis: dict[str, object],
) -> list[dict[str, object]]:
    scenes = analysis.get("scenes")

    if not isinstance(scenes, list):
        raise ValueError(
            "scene_analysis.json must contain "
            "a scenes list."
        )

    return [
        scene
        for scene in scenes
        if isinstance(scene, dict)
    ]


def _thumbnail_for_scene(
    *,
    scene: dict[str, object],
    analysis_path: Path,
    thumbnail_dir: Path | None,
) -> dict[str, object]:
    scene_number = int(
        scene["scene_number"]
    )
    scene_thumbnail = scene.get(
        "thumbnail_path"
    )

    if (
        isinstance(scene_thumbnail, str)
        and scene_thumbnail
    ):
        thumbnail_path = Path(
            scene_thumbnail
        )

        if not thumbnail_path.is_absolute():
            thumbnail_path = (
                analysis_path.parent
                / thumbnail_path
            )
    else:
        thumbnail_path = (
            _find_numbered_thumbnail(
                thumbnail_dir
                or analysis_path.parent
                / "thumbnails",
                scene_number,
            )
        )

    width, height = _image_dimensions(
        thumbnail_path
    )

    return {
        "scene_number": scene_number,
        "path": thumbnail_path,
        "width": width,
        "height": height,
    }


def _find_numbered_thumbnail(
    thumbnail_dir: Path,
    scene_number: int,
) -> Path:
    filename_stems = [
        f"scene_{scene_number:02d}",
        f"scene_{scene_number:03d}",
    ]

    for stem in filename_stems:
        for extension in THUMBNAIL_EXTENSIONS:
            candidate = (
                thumbnail_dir
                / f"{stem}{extension}"
            )

            if candidate.is_file():
                return candidate

    raise FileNotFoundError(
        f"Thumbnail for scene {scene_number} "
        f"was not found in {thumbnail_dir}."
    )


def _image_dimensions(
    path: Path,
) -> tuple[int, int]:
    if not path.is_file():
        raise FileNotFoundError(
            "Thumbnail file does not exist: "
            f"{path}"
        )

    suffix = path.suffix.lower()

    if suffix == ".png":
        return _png_dimensions(path)

    if suffix in (".jpg", ".jpeg"):
        return _jpeg_dimensions(path)

    raise ValueError(
        "Unsupported thumbnail extension: "
        f"{path.suffix}"
    )


def _png_dimensions(
    path: Path,
) -> tuple[int, int]:
    with path.open("rb") as file:
        header = file.read(24)

    if (
        len(header) < 24
        or not header.startswith(
            b"\x89PNG\r\n\x1a\n"
        )
    ):
        raise ValueError(
            f"Invalid PNG thumbnail: {path}"
        )

    return struct.unpack(
        ">II",
        header[16:24],
    )


def _jpeg_dimensions(
    path: Path,
) -> tuple[int, int]:
    with path.open("rb") as file:
        if file.read(2) != b"\xff\xd8":
            raise ValueError(
                f"Invalid JPEG thumbnail: {path}"
            )

        while True:
            marker_start = file.read(1)

            if marker_start == b"":
                break

            if marker_start != b"\xff":
                continue

            marker = file.read(1)

            while marker == b"\xff":
                marker = file.read(1)

            if marker in (
                b"\xc0",
                b"\xc2",
            ):
                segment = file.read(7)

                if len(segment) < 7:
                    break

                height, width = struct.unpack(
                    ">HH",
                    segment[3:7],
                )

                return width, height

            length_bytes = file.read(2)

            if len(length_bytes) < 2:
                break

            segment_length = struct.unpack(
                ">H",
                length_bytes,
            )[0]

            file.seek(
                segment_length - 2,
                1,
            )

    raise ValueError(
        "Could not read JPEG dimensions: "
        f"{path}"
    )


def _contact_sheet_svg(
    thumbnails: list[dict[str, object]],
) -> str:
    if not thumbnails:
        raise ValueError(
            "At least one scene thumbnail "
            "is required."
        )

    tile_width = 240
    tile_height = 180
    label_height = 32
    padding = 16
    columns = min(
        4,
        len(thumbnails),
    )
    rows = math.ceil(
        len(thumbnails) / columns
    )
    sheet_width = (
        columns * tile_width
        + (columns + 1) * padding
    )
    sheet_height = (
        rows * (
            tile_height
            + label_height
        )
        + (rows + 1) * padding
    )

    lines = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{sheet_width}" '
            f'height="{sheet_height}" '
            f'viewBox="0 0 {sheet_width} '
            f'{sheet_height}">'
        ),
        (
            '<rect width="100%" height="100%" '
            'fill="#111111"/>'
        ),
    ]

    for index, thumbnail in enumerate(
        thumbnails
    ):
        row, column = divmod(
            index,
            columns,
        )
        x = (
            padding
            + column
            * (
                tile_width
                + padding
            )
        )
        y = (
            padding
            + row
            * (
                tile_height
                + label_height
                + padding
            )
        )
        scene_number = int(
            thumbnail["scene_number"]
        )
        path = Path(
            thumbnail["path"]
        )

        lines.extend(
            [
                f'<g id="scene-{scene_number}">',
                (
                    f'<image href="'
                    f'{html.escape(path.as_posix())}" '
                    f'x="{x}" y="{y}" '
                    f'width="{tile_width}" '
                    f'height="{tile_height}" '
                    'preserveAspectRatio="'
                    'xMidYMid meet"/>'
                ),
                (
                    f'<rect x="{x}" y="{y}" '
                    'width="68" height="42" '
                    'fill="#000000" '
                    'opacity="0.72"/>'
                ),
                (
                    f'<text x="{x + 12}" '
                    f'y="{y + 29}" '
                    'fill="#ffffff" '
                    'font-family="Arial, sans-serif" '
                    'font-size="24" '
                    f'font-weight="700">'
                    f'{scene_number}</text>'
                ),
                (
                    f'<text x="{x}" '
                    f'y="{y + tile_height + 24}" '
                    'fill="#ffffff" '
                    'font-family="Arial, sans-serif" '
                    'font-size="16">'
                    f'Scene {scene_number}</text>'
                ),
                "</g>",
            ]
        )

    lines.append("</svg>")

    return "\n".join(lines) + "\n"


def _template_row(
    scene: dict[str, object],
) -> dict[str, object]:
    return {
        "scene_number": int(
            scene["scene_number"]
        ),
        "keep": False,
        "hook": False,
        "pour": False,
        "macro": False,
        "product": False,
        "cta": False,
        "watermark": "none",
        "subtitle_safe_zone": "bottom",
        "quality": 3,
        "food": False,
        "packaging": False,
        "human": False,
        "pouring": False,
        "macro_closeup": False,
        "reject_reason": "",
        "notes": "",
    }


def _template_json(
    scenes: list[dict[str, object]],
) -> str:
    return json.dumps(
        [
            _template_row(scene)
            for scene in scenes
        ],
        indent=2,
        sort_keys=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
