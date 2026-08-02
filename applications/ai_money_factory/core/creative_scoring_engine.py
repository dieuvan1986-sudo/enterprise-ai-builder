from __future__ import annotations

from dataclasses import dataclass

from applications.ai_money_factory.core.creative_engine import (
    CreativeConcept,
)


@dataclass(slots=True)
class CreativeScore:
    concept: CreativeConcept
    hook_score: float
    visual_score: float
    conversion_score: float
    brand_fit_score: float
    claim_safety_score: float
    total_score: float
    status: str
    warnings: list[str]


class CreativeScoringEngine:
    """
    Score and rank creative concepts before production.

    Claim safety acts as a gate:
    a commercially attractive concept must not automatically
    proceed to production when its claims need verification.
    """

    def score(self, concept: CreativeConcept) -> CreativeScore:
        hook_score = self._score_hook(concept)
        visual_score = self._score_visual(concept)
        conversion_score = self._score_conversion(concept)
        brand_fit_score = self._score_brand_fit(concept)

        claim_safety_score, warnings = self._score_claim_safety(
            concept
        )

        total_score = (
            hook_score * 0.25
            + visual_score * 0.20
            + conversion_score * 0.20
            + brand_fit_score * 0.15
            + claim_safety_score * 0.20
        )

        if claim_safety_score < 7:
            status = "NEEDS_REVIEW"
        elif total_score >= 8:
            status = "READY"
        elif total_score >= 6.5:
            status = "PROMISING"
        else:
            status = "REJECT"

        return CreativeScore(
            concept=concept,
            hook_score=round(hook_score, 2),
            visual_score=round(visual_score, 2),
            conversion_score=round(conversion_score, 2),
            brand_fit_score=round(brand_fit_score, 2),
            claim_safety_score=round(claim_safety_score, 2),
            total_score=round(total_score, 2),
            status=status,
            warnings=warnings,
        )

    def rank(
        self,
        concepts: list[CreativeConcept],
    ) -> list[CreativeScore]:
        results = [
            self.score(concept)
            for concept in concepts
        ]

        results.sort(
            key=lambda result: (
                result.status == "READY",
                result.status == "PROMISING",
                result.total_score,
            ),
            reverse=True,
        )

        return results

    @staticmethod
    def _score_hook(concept: CreativeConcept) -> float:
        hook = concept.hook.strip()
        word_count = len(hook.split())

        score = 7.0

        if 4 <= word_count <= 12:
            score += 1.5

        if "?" in hook:
            score += 0.5

        attention_terms = (
            "khoan",
            "đừng",
            "thử",
            "tại sao",
            "chưa",
            "64",
        )

        if any(
            term in hook.lower()
            for term in attention_terms
        ):
            score += 1.0

        return min(score, 10.0)

    @staticmethod
    def _score_visual(concept: CreativeConcept) -> float:
        text = concept.visual_idea.lower()
        score = 6.0

        visual_terms = (
            "cận cảnh",
            "top-down",
            "cut",
            "lia máy",
            "rót",
            "tay",
            "không lộ mặt",
            "focus",
        )

        matches = sum(
            term in text
            for term in visual_terms
        )

        score += min(matches * 0.6, 4.0)

        return min(score, 10.0)

    @staticmethod
    def _score_conversion(concept: CreativeConcept) -> float:
        score = 6.5
        cta = concept.cta.lower()

        soft_cta_terms = (
            "tham khảo",
            "xem sản phẩm",
            "giỏ hàng",
            "lưu lại",
            "cân nhắc",
        )

        if any(
            term in cta
            for term in soft_cta_terms
        ):
            score += 1.5

        if concept.target_audience.strip():
            score += 1.0

        if concept.angle.strip():
            score += 0.5

        return min(score, 10.0)

    @staticmethod
    def _score_brand_fit(concept: CreativeConcept) -> float:
        score = 7.0

        if concept.target_audience.strip():
            score += 1.0

        if concept.visual_idea.strip():
            score += 1.0

        if len(concept.script) >= 3:
            score += 0.5

        return min(score, 10.0)

    @staticmethod
    def _score_claim_safety(
        concept: CreativeConcept,
    ) -> tuple[float, list[str]]:
        text = " ".join(
            [
                concept.hook,
                *concept.script,
                concept.cta,
            ]
        ).lower()

        warnings: list[str] = []
        score = 10.0

        risky_phrases = {
            "hợp để": (
                "Công dụng/cách sử dụng cần xác minh."
            ),
            "dùng để": (
                "Mục đích sử dụng cần dữ liệu sản phẩm xác minh."
            ),
            "tốt cho": (
                "Claim lợi ích cần bằng chứng."
            ),
            "giúp": (
                "Claim lợi ích cần được kiểm chứng."
            ),
            "hiệu quả": (
                "Claim hiệu quả cần bằng chứng."
            ),
            "bán chạy": (
                "Claim thị trường cần nguồn dữ liệu."
            ),
            "nhiều người mua": (
                "Claim thị trường cần nguồn dữ liệu."
            ),
        }

        for phrase, warning in risky_phrases.items():
            if phrase in text:
                warnings.append(warning)
                score -= 2.0

        return max(score, 0.0), warnings
