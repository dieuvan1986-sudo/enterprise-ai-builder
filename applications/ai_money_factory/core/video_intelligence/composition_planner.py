from __future__ import annotations

from applications.ai_money_factory.core.video_intelligence.models import (
    CompositionPlan,
    CompositionSegmentPlan,
    NarrativeBeat,
    SelectedTimelineClip,
    SubtitleSegmentPlan,
    VoiceSegmentPlan,
)

PURPOSE_ORDER = ("HOOK", "POUR", "MACRO", "PRODUCT", "CTA")
TIMING_TOLERANCE_SECONDS = 0.001
LANGUAGE = "vi-VN"
GENDER = "female"
ACCENT = "northern_standard"
VOICE_ID = "vi-VN-HoaiMyNeural"
UNSAFE_WATERMARKS = {"major", "center", "reject"}


class CompositionPlanner:
    """
    Build deterministic render-readiness metadata for a planned short video.
    """

    def plan(
        self,
        clips: list[SelectedTimelineClip],
        beats: list[NarrativeBeat],
        voice_segments: list[VoiceSegmentPlan],
        subtitle_segments: list[SubtitleSegmentPlan],
    ) -> CompositionPlan:
        _validate_inputs(clips, beats, voice_segments, subtitle_segments)

        segments = [
            _composition_segment_from_records(clip, beat, voice_segment, subtitle_segment)
            for clip, beat, voice_segment, subtitle_segment in zip(
                clips,
                beats,
                voice_segments,
                subtitle_segments,
                strict=True,
            )
        ]
        blocking_reasons = _plan_blocking_reasons(segments)
        total_duration = segments[-1].output_end_seconds if segments else 0.0

        return CompositionPlan(
            segments=segments,
            total_duration_seconds=total_duration,
            render_ready=not blocking_reasons,
            blocking_reasons=blocking_reasons,
            target_width=1080,
            target_height=1920,
            fps=30,
            video_codec="libx264",
            audio_codec="aac",
            pixel_format="yuv420p",
            confidence=_plan_confidence(segments),
        )


def _validate_inputs(
    clips: list[SelectedTimelineClip],
    beats: list[NarrativeBeat],
    voice_segments: list[VoiceSegmentPlan],
    subtitle_segments: list[SubtitleSegmentPlan],
) -> None:
    _validate_collection("timeline clips", clips)
    _validate_collection("narrative beats", beats)
    _validate_collection("voice segments", voice_segments)
    _validate_collection("subtitle segments", subtitle_segments)
    _validate_record_alignment(clips, beats, voice_segments, subtitle_segments)
    _validate_timing(clips, voice_segments, subtitle_segments)
    _validate_voice_safety(voice_segments)
    _validate_subtitle_safety(subtitle_segments)

    for clip in clips:
        if clip.duration_seconds <= 0:
            raise ValueError(f"scene {clip.scene_number} duration must be positive.")

        if clip.source_end_seconds <= clip.source_start_seconds:
            raise ValueError(f"scene {clip.scene_number} source end must be after start.")

        if not 0.0 <= clip.confidence <= 1.0:
            raise ValueError(
                f"scene {clip.scene_number} clip confidence must be between 0.0 and 1.0."
            )

    for beat in beats:
        if not 0.0 <= beat.confidence <= 1.0:
            raise ValueError(
                f"scene {beat.scene_number} beat confidence must be between 0.0 and 1.0."
            )


def _validate_collection(
    label: str,
    records: (
        list[SelectedTimelineClip]
        | list[NarrativeBeat]
        | list[VoiceSegmentPlan]
        | list[SubtitleSegmentPlan]
    ),
) -> None:
    if len(records) != len(PURPOSE_ORDER):
        raise ValueError(f"{label} must contain exactly five records.")

    purposes = [record.purpose for record in records]
    duplicate_purposes = [
        purpose
        for purpose in PURPOSE_ORDER
        if purposes.count(purpose) > 1
    ]

    if duplicate_purposes:
        raise ValueError(f"{label} contains duplicate purpose {duplicate_purposes[0]}.")

    missing_purposes = sorted(set(PURPOSE_ORDER) - set(purposes))

    if missing_purposes:
        raise ValueError(f"{label} is missing purpose {missing_purposes[0]}.")

    if purposes != list(PURPOSE_ORDER):
        raise ValueError(
            f"{label} purpose order must be HOOK, POUR, MACRO, PRODUCT, CTA."
        )


def _validate_record_alignment(
    clips: list[SelectedTimelineClip],
    beats: list[NarrativeBeat],
    voice_segments: list[VoiceSegmentPlan],
    subtitle_segments: list[SubtitleSegmentPlan],
) -> None:
    for index, records in enumerate(
        zip(clips, beats, voice_segments, subtitle_segments, strict=True),
        start=1,
    ):
        scene_numbers = {record.scene_number for record in records}

        if len(scene_numbers) != 1:
            raise ValueError(f"record {index} scene_number values must match.")

        purposes = {record.purpose for record in records}

        if len(purposes) != 1:
            raise ValueError(f"record {index} purpose values must match.")


def _validate_timing(
    clips: list[SelectedTimelineClip],
    voice_segments: list[VoiceSegmentPlan],
    subtitle_segments: list[SubtitleSegmentPlan],
) -> None:
    previous_end = 0.0

    for index, (clip, voice_segment, subtitle_segment) in enumerate(
        zip(clips, voice_segments, subtitle_segments, strict=True),
        start=1,
    ):
        if clip.output_end_seconds <= clip.output_start_seconds:
            raise ValueError(
                f"clip {index} output_end_seconds must be greater than output_start_seconds."
            )

        if abs(clip.output_start_seconds - previous_end) > TIMING_TOLERANCE_SECONDS:
            relation = "gap" if clip.output_start_seconds > previous_end else "overlap"
            raise ValueError(f"composition timing has a timing {relation} before clip {index}.")

        duration = clip.output_end_seconds - clip.output_start_seconds

        if abs(duration - clip.target_duration_seconds) > TIMING_TOLERANCE_SECONDS:
            raise ValueError(
                f"clip {index} target_duration_seconds must equal output duration."
            )

        _validate_segment_timing("voice segment", index, voice_segment.start_seconds, voice_segment.end_seconds, voice_segment.duration_seconds, clip)
        _validate_segment_timing("subtitle segment", index, subtitle_segment.start_seconds, subtitle_segment.end_seconds, subtitle_segment.duration_seconds, clip)
        previous_end = clip.output_end_seconds


def _validate_segment_timing(
    label: str,
    index: int,
    start_seconds: float,
    end_seconds: float,
    duration_seconds: float,
    clip: SelectedTimelineClip,
) -> None:
    if end_seconds <= start_seconds:
        raise ValueError(f"{label} {index} end_seconds must be greater than start_seconds.")

    if duration_seconds <= 0:
        raise ValueError(f"{label} {index} duration must be positive.")

    if abs(start_seconds - clip.output_start_seconds) > TIMING_TOLERANCE_SECONDS:
        raise ValueError(f"{label} {index} start_seconds must match clip timing.")

    if abs(end_seconds - clip.output_end_seconds) > TIMING_TOLERANCE_SECONDS:
        raise ValueError(f"{label} {index} end_seconds must match clip timing.")

    if abs((end_seconds - start_seconds) - duration_seconds) > TIMING_TOLERANCE_SECONDS:
        raise ValueError(f"{label} {index} duration_seconds must equal output duration.")


def _validate_voice_safety(voice_segments: list[VoiceSegmentPlan]) -> None:
    for segment in voice_segments:
        if segment.language != LANGUAGE:
            raise ValueError("voice language must remain vi-VN.")

        if segment.gender != GENDER:
            raise ValueError("voice gender must remain female.")

        if segment.accent != ACCENT:
            raise ValueError("voice accent must remain northern_standard.")

        if segment.voice_id != VOICE_ID:
            raise ValueError("voice_id must remain vi-VN-HoaiMyNeural.")

        if not 0.0 <= segment.confidence <= 1.0:
            raise ValueError(
                f"voice segment {segment.scene_number} confidence must be between 0.0 and 1.0."
            )


def _validate_subtitle_safety(subtitle_segments: list[SubtitleSegmentPlan]) -> None:
    for segment in subtitle_segments:
        if segment.max_lines > 2:
            raise ValueError(
                f"subtitle segment {segment.scene_number} max_lines must not exceed 2."
            )

        if segment.anchor == "center_center":
            raise ValueError(
                f"subtitle segment {segment.scene_number} anchor must not be center_center."
            )

        if not 0.0 <= segment.confidence <= 1.0:
            raise ValueError(
                "subtitle segment "
                f"{segment.scene_number} confidence must be between 0.0 and 1.0."
            )


def _composition_segment_from_records(
    clip: SelectedTimelineClip,
    beat: NarrativeBeat,
    voice_segment: VoiceSegmentPlan,
    subtitle_segment: SubtitleSegmentPlan,
) -> CompositionSegmentPlan:
    blocking_reasons = _segment_blocking_reasons(clip, voice_segment, subtitle_segment)

    return CompositionSegmentPlan(
        scene_number=clip.scene_number,
        purpose=clip.purpose,
        source_path=clip.source_path,
        source_start_seconds=clip.source_start_seconds,
        source_end_seconds=clip.source_end_seconds,
        output_start_seconds=clip.output_start_seconds,
        output_end_seconds=clip.output_end_seconds,
        duration_seconds=clip.duration_seconds,
        target_duration_seconds=clip.target_duration_seconds,
        voice_start_seconds=voice_segment.start_seconds,
        voice_end_seconds=voice_segment.end_seconds,
        subtitle_start_seconds=subtitle_segment.start_seconds,
        subtitle_end_seconds=subtitle_segment.end_seconds,
        language=voice_segment.language,
        gender=voice_segment.gender,
        accent=voice_segment.accent,
        voice_id=voice_segment.voice_id,
        subtitle_anchor=subtitle_segment.anchor,
        subtitle_max_lines=subtitle_segment.max_lines,
        watermark=clip.watermark,
        crop_required=clip.watermark == "croppable" or clip.requires_crop,
        render_ready=not blocking_reasons,
        blocking_reasons=blocking_reasons,
        confidence=min(
            clip.confidence,
            beat.confidence,
            voice_segment.confidence,
            subtitle_segment.confidence,
        ),
    )


def _segment_blocking_reasons(
    clip: SelectedTimelineClip,
    voice_segment: VoiceSegmentPlan,
    subtitle_segment: SubtitleSegmentPlan,
) -> list[str]:
    reasons = []

    if clip.watermark in UNSAFE_WATERMARKS:
        reasons.append(f"unsafe watermark: {clip.watermark}")

    if voice_segment.language != LANGUAGE:
        reasons.append("voice language is not vi-VN")

    if voice_segment.gender != GENDER:
        reasons.append("voice gender is not female")

    if voice_segment.accent != ACCENT:
        reasons.append("voice accent is not northern_standard")

    if voice_segment.voice_id != VOICE_ID:
        reasons.append("voice_id is not vi-VN-HoaiMyNeural")

    if subtitle_segment.max_lines > 2:
        reasons.append("subtitle max_lines exceeds 2")

    if subtitle_segment.anchor == "center_center":
        reasons.append("subtitle anchor is center_center")

    return reasons


def _plan_blocking_reasons(segments: list[CompositionSegmentPlan]) -> list[str]:
    reasons = []

    for segment in segments:
        for reason in segment.blocking_reasons:
            message = f"scene {segment.scene_number}: {reason}"

            if message not in reasons:
                reasons.append(message)

    return reasons


def _plan_confidence(segments: list[CompositionSegmentPlan]) -> float:
    if not segments:
        return 0.0

    return min(segment.confidence for segment in segments)
