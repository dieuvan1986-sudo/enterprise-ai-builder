from __future__ import annotations

from applications.ai_money_factory.core.content_models import (
    ContentAngle,
    VideoMission,
    VideoScript,
    VisualScene,
)
from applications.ai_money_factory.core.opportunity_engine import Product


class ContentStrategyEngine:
    """
    Build an initial short-form affiliate video mission from a product.

    MVP uses deterministic strategy rules.
    A future AI provider will generate and optimize creative variants
    without changing the VideoMission contract.
    """

    def generate(self, product: Product) -> VideoMission:
        angle = self._select_angle(product)
        script = self._build_script(product, angle)
        scenes = self._build_scenes(product, script)

        return VideoMission(
            product_name=product.name,
            angle=angle,
            script=script,
            scenes=scenes,
            caption=self._build_caption(product),
            hashtags=self._build_hashtags(product),
        )

    def _select_angle(self, product: Product) -> ContentAngle:
        if product.demand_score >= 8 and product.trend_score >= 8:
            return ContentAngle(
                name="TREND_PROOF",
                description=(
                    "Use strong market demand and trend signals "
                    "to create curiosity and social proof."
                ),
                target_audience="Nguoi dang tim mon hot va dang duoc mua nhieu",
                pain_point="Khong biet san pham dang hot co thuc su dang thu",
                promise="Xem nhanh ly do san pham nay dang duoc chu y",
            )

        if product.video_score >= 8:
            return ContentAngle(
                name="VISUAL_DEMO",
                description="Show the product benefit through visual demonstration.",
                target_audience="Nguoi thich xem demo san pham nhanh",
                pain_point="Kho hinh dung san pham co huu ich hay khong",
                promise="Cho thay cong dung san pham trong vai giay",
            )

        return ContentAngle(
            name="PROBLEM_SOLUTION",
            description="Introduce a common problem and position the product as a solution.",
            target_audience="Nguoi mua sam online",
            pain_point="Can mot giai phap don gian cho nhu cau hang ngay",
            promise="Mot lua chon dang tham khao voi muc gia de tiep can",
        )

    def _build_script(
        self,
        product: Product,
        angle: ContentAngle,
    ) -> VideoScript:
        hook = (
            f"Tai sao {product.name} lai dang duoc nhieu nguoi chu y?"
        )

        body = [
            (
                f"San pham nay dang co diem xu huong "
                f"{product.trend_score}/10."
            ),
            (
                f"Nhu cau thi truong duoc he thong cham "
                f"{product.demand_score}/10."
            ),
            (
                f"Gia tham khao hien tai khoang "
                f"{product.price:,.0f} dong."
            ),
            angle.promise + ".",
        ]

        cta = "Xem thong tin san pham o lien ket tren kenh."

        return VideoScript(
            hook=hook,
            body=body,
            cta=cta,
            duration_seconds=25,
        )

    def _build_scenes(
        self,
        product: Product,
        script: VideoScript,
    ) -> list[VisualScene]:
        voice_lines = [
            script.hook,
            *script.body,
            script.cta,
        ]

        scenes: list[VisualScene] = []

        for index, voiceover in enumerate(voice_lines, start=1):
            scenes.append(
                VisualScene(
                    order=index,
                    duration_seconds=4,
                    visual_prompt=(
                        f"Vertical 9:16 commercial product video featuring "
                        f"{product.name}, clean modern composition, "
                        f"strong product focus, realistic lighting, "
                        f"social commerce short video style"
                    ),
                    voiceover=voiceover,
                    on_screen_text=self._short_text(
                        voiceover
                    ),
                )
            )

        return scenes

    @staticmethod
    def _short_text(text: str) -> str:
        words = text.split()

        if len(words) <= 7:
            return text

        return " ".join(words[:7]) + "..."

    @staticmethod
    def _build_caption(product: Product) -> str:
        return (
            f"{product.name} dang duoc chu y. "
            "Xem nhanh truoc khi quyet dinh mua."
        )

    @staticmethod
    def _build_hashtags(product: Product) -> list[str]:
        return [
            "#MonHay365",
            "#ReviewSanPham",
            "#ShopeeFinds",
            "#DoHayMoiNgay",
        ]
