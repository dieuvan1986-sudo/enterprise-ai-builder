from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

from applications.ai_money_factory.tools.review_scene_sheet import main


def test_review_scene_sheet_writes_contact_sheet_and_template(
    tmp_path: Path,
    capsys,
) -> None:
    thumbnail_dir = tmp_path / "thumbnails"
    thumbnail_dir.mkdir()
    _write_jpeg(thumbnail_dir / "scene_01.jpg", width=20, height=10)
    _write_jpeg(thumbnail_dir / "scene_02.jpg", width=20, height=10)
    analysis_path = tmp_path / "scene_analysis.json"
    _write_analysis(analysis_path, scene_count=2)

    result = main([str(analysis_path)])

    contact_sheet_path = tmp_path / "scene_review_contact_sheet.svg"
    template_path = tmp_path / "scene_review_template.json"

    assert result == 0
    assert capsys.readouterr().out == (
        f"Wrote {contact_sheet_path}\n"
        f"Wrote {template_path}\n"
    )
    assert contact_sheet_path.is_file()
    assert template_path.is_file()
    assert contact_sheet_path.read_text(encoding="utf-8") == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="528" '
        'height="244" viewBox="0 0 528 244">\n'
        '<rect width="100%" height="100%" fill="#111111"/>\n'
        '<g id="scene-1">\n'
        f'<image href="{(thumbnail_dir / "scene_01.jpg").as_posix()}" '
        'x="16" y="16" width="240" height="180" '
        'preserveAspectRatio="xMidYMid meet"/>\n'
        '<rect x="16" y="16" width="68" height="42" '
        'fill="#000000" opacity="0.72"/>\n'
        '<text x="28" y="45" fill="#ffffff" '
        'font-family="Arial, sans-serif" font-size="24" '
        'font-weight="700">1</text>\n'
        '<text x="16" y="220" fill="#ffffff" '
        'font-family="Arial, sans-serif" font-size="16">Scene 1</text>\n'
        '</g>\n'
        '<g id="scene-2">\n'
        f'<image href="{(thumbnail_dir / "scene_02.jpg").as_posix()}" '
        'x="272" y="16" width="240" height="180" '
        'preserveAspectRatio="xMidYMid meet"/>\n'
        '<rect x="272" y="16" width="68" height="42" '
        'fill="#000000" opacity="0.72"/>\n'
        '<text x="284" y="45" fill="#ffffff" '
        'font-family="Arial, sans-serif" font-size="24" '
        'font-weight="700">2</text>\n'
        '<text x="272" y="220" fill="#ffffff" '
        'font-family="Arial, sans-serif" font-size="16">Scene 2</text>\n'
        '</g>\n'
        '</svg>\n'
    )
    assert json.loads(template_path.read_text(encoding="utf-8")) == [
        _expected_template_row(scene_number=1),
        _expected_template_row(scene_number=2),
    ]


def test_review_scene_sheet_preserves_existing_template_without_force(
    tmp_path: Path,
    capsys,
) -> None:
    thumbnail_dir = tmp_path / "thumbnails"
    thumbnail_dir.mkdir()
    _write_jpeg(thumbnail_dir / "scene_01.jpg", width=20, height=10)
    analysis_path = tmp_path / "scene_analysis.json"
    template_path = tmp_path / "scene_review_template.json"
    labeled_template = (
        '[{"scene_number":1,"keep":true,"hook":true,'
        '"watermark":"minor","subtitle_safe_zone":"top",'
        '"quality":5,"notes":"approved"}]\n'
    )
    _write_analysis(analysis_path, scene_count=1)
    template_path.write_text(labeled_template, encoding="utf-8")

    result = main([str(analysis_path)])

    contact_sheet_path = tmp_path / "scene_review_contact_sheet.svg"

    assert result == 0
    assert capsys.readouterr().out == (
        f"Wrote {contact_sheet_path}\n"
        f"Scene review template already exists: {template_path}\n"
        "Use --force to overwrite.\n"
    )
    assert contact_sheet_path.is_file()
    assert template_path.read_text(encoding="utf-8") == labeled_template


def test_review_scene_sheet_overwrites_existing_template_with_force(
    tmp_path: Path,
    capsys,
) -> None:
    thumbnail_dir = tmp_path / "thumbnails"
    thumbnail_dir.mkdir()
    _write_jpeg(thumbnail_dir / "scene_01.jpg", width=20, height=10)
    analysis_path = tmp_path / "scene_analysis.json"
    template_path = tmp_path / "scene_review_template.json"
    _write_analysis(analysis_path, scene_count=1)
    template_path.write_text(
        '[{"scene_number":1,"keep":true,"notes":"approved"}]\n',
        encoding="utf-8",
    )

    result = main([str(analysis_path), "--force"])

    contact_sheet_path = tmp_path / "scene_review_contact_sheet.svg"

    assert result == 0
    assert capsys.readouterr().out == (
        f"Wrote {contact_sheet_path}\n"
        f"Wrote {template_path}\n"
    )
    assert json.loads(template_path.read_text(encoding="utf-8")) == [
        _expected_template_row(scene_number=1),
    ]


def _write_analysis(path: Path, *, scene_count: int) -> None:
    scenes = []

    for scene_number in range(1, scene_count + 1):
        scenes.append(
            {
                "source_path": str(path.parent / "source.mp4"),
                "scene_number": scene_number,
                "start_seconds": (scene_number - 1) * 2,
                "end_seconds": scene_number * 2,
                "duration_seconds": 2,
            }
        )

    path.write_text(
        json.dumps(
            {
                "source": {
                    "path": str(path.parent / "source.mp4"),
                    "duration_seconds": scene_count * 2,
                    "width": 1080,
                    "height": 1920,
                    "fps": 30.0,
                },
                "scenes": scenes,
                "durations": {
                    "source_seconds": scene_count * 2,
                    "detected_scene_seconds": [2] * scene_count,
                    "total_detected_scene_seconds": scene_count * 2,
                },
            }
        ),
        encoding="utf-8",
    )


def _expected_template_row(*, scene_number: int) -> dict[str, object]:
    return {
        "scene_number": scene_number,
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


def _write_jpeg(path: Path, *, width: int, height: int) -> None:
    payload = (
        b"\xff\xd8"
        + _jpeg_segment(
            b"\xe0",
            b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00",
        )
        + _jpeg_segment(
            b"\xc0",
            b"\x08"
            + struct.pack(">HH", height, width)
            + b"\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00",
        )
        + b"\xff\xd9"
    )
    path.write_bytes(payload)


def _jpeg_segment(marker: bytes, data: bytes) -> bytes:
    return b"\xff" + marker + struct.pack(">H", len(data) + 2) + data


def _write_png(path: Path, *, width: int, height: int) -> None:
    raw_scanlines = b"".join(
        b"\x00" + b"\xff\xff\xff" * width
        for _ in range(height)
    )
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(
            b"IHDR",
            struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0),
        )
        + _png_chunk(b"IDAT", zlib.compress(raw_scanlines))
        + _png_chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF

    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", checksum)
    )
