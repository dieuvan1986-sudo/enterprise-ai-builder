from __future__ import annotations

import pytest

from applications.ai_money_factory.core.content_models import (
    Narration,
    NarrationSegment,
    SubtitleTrack,
    VoiceTrack,
    VoiceTrackSegment,
)
from applications.ai_money_factory.core.subtitle_renderer import (
    SubtitleRenderError,
    SubtitleRenderResult,
    SubtitleRenderer,
)
from applications.ai_money_factory.core.video_factory import (
    VideoPackage,
    VideoScene,
)


def test_render_narration_returns_subtitle_track() -> None:
    narration = Narration(
        title="Honey chili hook",
        segments=[
            NarrationSegment(
                scene_number=1,
                duration_seconds=3,
                text="Stop scrolling. This sauce changes dinner.",
                purpose="HOOK",
            ),
            NarrationSegment(
                scene_number=2,
                duration_seconds=5,
                text="Pour it over crispy chicken and watch it glaze.",
                purpose="POUR",
            ),
        ],
        total_duration_seconds=8,
    )

    track = SubtitleRenderer(max_chars_per_cue=24).render(narration)

    assert isinstance(track, SubtitleTrack)
    assert track.title == narration.title
    assert track.total_duration_seconds == 8
    assert [cue.scene_number for cue in track.cues] == [1, 1, 1, 2, 2, 2]
    assert [cue.cue_number for cue in track.cues] == [1, 2, 3, 4, 5, 6]
    assert track.cues[0].start_seconds == 0
    assert track.cues[-1].end_seconds == 8
    assert all(
        cue.end_seconds - cue.start_seconds >= 0.8
        for cue in track.cues
    )


def test_render_voice_track_uses_voice_narration() -> None:
    voice_track = VoiceTrack(
        title="Rendered voice",
        segments=[
            VoiceTrackSegment(
                scene_number=1,
                duration_seconds=4,
                narration="Clean audio becomes clean subtitles.",
                purpose="HOOK",
            )
        ],
        total_duration_seconds=4,
    )

    track = SubtitleRenderer().render(voice_track)

    assert isinstance(track, SubtitleTrack)
    assert track.cues[0].text == "Clean audio becomes clean subtitles."
    assert track.cues[0].end_seconds == 4


def test_render_video_package_preserves_public_api() -> None:
    package = VideoPackage(
        title="Legacy package",
        hook="Hook",
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
                purpose="CTA",
                narration="Tap to see it.",
                visual_prompt="Visual two",
            ),
        ],
        cta="CTA",
        total_duration_seconds=8,
    )

    result = SubtitleRenderer().render(package)

    assert isinstance(result, SubtitleRenderResult)
    assert result.total_duration_seconds == 8
    assert [scene.purpose for scene in result.scenes] == ["HOOK", "CTA"]
    assert [cue.text for cue in result.cues] == ["Start here.", "Tap to see it."]


def test_render_rejects_unreadably_short_segments() -> None:
    narration = Narration(
        title="Too short",
        segments=[
            NarrationSegment(
                scene_number=1,
                duration_seconds=0.5,
                text="Too many words for this tiny timing window.",
            )
        ],
    )

    renderer = SubtitleRenderer(max_chars_per_cue=12, min_cue_seconds=0.8)

    with pytest.raises(SubtitleRenderError, match="too short"):
        renderer.render(narration)
