from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from applications.ai_money_factory.core.openclaw_creative_provider import (
    OpenClawCreativeProvider,
)
from applications.ai_money_factory.core.opportunity_engine import Product


@dataclass(slots=True)
class CreativeConcept:
    name: str
    angle: str
    hook: str
    script: list[str]
    cta: str
    visual_idea: str
    target_audience: str


class CreativeEngine:
    """
    Generate structured TikTok affiliate concepts through GPT-5.5.

    Spoken/written product claims must stay inside verified_facts.
    Product-use visuals must stay inside verified_visual_facts.
    """

    def __init__(
        self,
        provider: OpenClawCreativeProvider,
    ) -> None:
        self.provider = provider

    def generate_concepts(
        self,
        product: Product,
        count: int = 3,
    ) -> list[CreativeConcept]:
        if count < 1:
            raise ValueError("Concept count must be at least 1.")

        prompt = self._build_prompt(product, count)
        response = self.provider.generate(prompt)

        return self._parse_concepts(response, count)

    @staticmethod
    def _build_prompt(
        product: Product,
        count: int,
    ) -> str:
        if product.verified_facts:
            verified_facts = "\n".join(
                f"- {fact}"
                for fact in product.verified_facts
            )
        else:
            verified_facts = (
                "- CHƯA CÓ FACT SẢN PHẨM NÀO ĐƯỢC XÁC MINH."
            )

        if product.verified_visual_facts:
            verified_visual_facts = "\n".join(
                f"- {fact}"
                for fact in product.verified_visual_facts
            )
        else:
            verified_visual_facts = (
                "- CHƯA CÓ VISUAL FACT NÀO ĐƯỢC XÁC MINH."
            )

        if product.price_verified:
            price_context = (
                f"- Giá đã xác minh gần đây: "
                f"{product.price:,.0f} VNĐ"
            )
        else:
            price_context = (
                "- Giá CHƯA được xác minh gần đây. "
                "KHÔNG được nhắc giá cụ thể trong nội dung."
            )

        source_context = (
            product.fact_source
            if product.fact_source
            else "Chưa có nguồn fact được ghi nhận"
        )

        return f"""
Bạn là Creative Strategist chuyên TikTok Affiliate cho kênh MÓN HAY 365.

MỤC TIÊU KINH DOANH:
Tạo concept video có khả năng giữ người xem, kích thích quan tâm
đến sản phẩm và hỗ trợ chuyển đổi Affiliate, nhưng tuyệt đối
không bịa claim sản phẩm.

NHIỆM VỤ:
Tạo {count} concept video TikTok KHÁC NHAU cho sản phẩm dưới đây.

THÔNG TIN NHẬN DIỆN:
- Tên sản phẩm: {product.name}
- Danh mục: {product.category}

FACT WHITELIST ĐÃ XÁC MINH:
{verified_facts}

VERIFIED VISUAL FACTS:
{verified_visual_facts}

NGUỒN FACT:
- {source_context}

TRẠNG THÁI GIÁ:
{price_context}

TÍN HIỆU CHIẾN LƯỢC NỘI BỘ:
- Trend score: {product.trend_score}/10
- Demand score: {product.demand_score}/10
- Video score: {product.video_score}/10
- Competition score: {product.competition_score}/10

NGUYÊN TẮC CREATIVE:
1. Hook phải tạo điểm dừng mạnh trong 2-3 giây đầu.
2. Ưu tiên visual-first: hình ảnh phải hấp dẫn ngay cả khi tắt tiếng.
3. Với sản phẩm thực phẩm, nếu VERIFIED VISUAL FACTS cho phép,
   ưu tiên macro food shot, texture, chuyển động, rưới, chấm,
   close-up và các cảnh món ăn hấp dẫn.
4. Không mở đầu bằng cảnh bao bì tĩnh nếu có visual mạnh hơn
   đã được VERIFIED VISUAL FACTS cho phép.
5. Bao bì/sản phẩm nên xuất hiện rõ trong video để người xem
   nhận diện được sản phẩm.
6. Ưu tiên video không cần lộ mặt và có thể sản xuất bằng AI Video.
7. Mỗi concept phải khác angle, không chỉ thay câu chữ.
8. Script phù hợp video khoảng 20-30 giây.
9. CTA tự nhiên, hướng người xem tới trang/giỏ sản phẩm
   nhưng không ép mua.

QUY TẮC FACT SAFETY:
10. FACT WHITELIST kiểm soát những gì được phép NÓI hoặc VIẾT
    như một sự thật về sản phẩm.
11. VERIFIED VISUAL FACTS kiểm soát những gì được phép THỂ HIỆN
    bằng hình ảnh về sản phẩm.
12. Không biến một visual fact thành claim bằng lời nếu claim đó
    không nằm trong FACT WHITELIST.
13. Không tự suy diễn công dụng, thành phần, hương vị, chất lượng,
    lợi ích sức khỏe, đối tượng sử dụng, bảo quản, doanh số,
    đánh giá hoặc độ phổ biến.
14. Không tự tạo before/after hoặc kết quả sử dụng chưa xác minh.
15. Không biến trend score, demand score, video score hoặc
    competition score thành bằng chứng nói với người xem.
16. Nếu giá chưa xác minh, tuyệt đối không nhắc mức giá cụ thể
    trong hook, script, CTA hoặc visual.
17. Nếu VERIFIED VISUAL FACTS trống, không được mô phỏng cách dùng
    sản phẩm; chỉ được dùng bao bì hoặc visual trung tính.
18. Nếu VERIFIED VISUAL FACTS cho phép cảnh rưới/chấm cùng món ăn,
    được phép sáng tạo góc máy và bố cục của cảnh đó nhưng không
    được thêm claim chưa xác minh.
19. Không sao chép nguyên hook, script, caption hoặc cách thể hiện
    đặc trưng của một creator/đối thủ cụ thể.
20. Sáng tạo dựa trên pattern hiệu quả, không sao chép nội dung.

YÊU CẦU VISUAL:
- visual_idea phải đủ cụ thể để AI Video Factory dựng thành scene.
- Mô tả rõ cảnh mở đầu.
- Mô tả chuyển động chính.
- Mô tả close-up/macro khi phù hợp.
- Mô tả vị trí xuất hiện của sản phẩm.
- Ưu tiên hành động và chuyển động thay vì cảnh tĩnh.
- Không yêu cầu AI tạo chữ giá nếu giá chưa xác minh.

CHỈ TRẢ VỀ JSON HỢP LỆ.
Không markdown.
Không ```json.
Không giải thích thêm.

Schema bắt buộc:
{{
  "concepts": [
    {{
      "name": "Tên concept ngắn",
      "angle": "Góc tiếp cận",
      "hook": "Câu hook",
      "script": [
        "Câu thoại 1",
        "Câu thoại 2",
        "Câu thoại 3"
      ],
      "cta": "CTA",
      "visual_idea": "Ý tưởng video cụ thể cho AI Video Factory",
      "target_audience": "Nhóm người xem"
    }}
  ]
}}
""".strip()

    @staticmethod
    def _parse_concepts(
        response: str,
        expected_count: int,
    ) -> list[CreativeConcept]:
        try:
            payload: dict[str, Any] = json.loads(response)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Creative AI returned invalid JSON."
            ) from exc

        raw_concepts = payload.get("concepts")

        if not isinstance(raw_concepts, list):
            raise RuntimeError(
                "Creative AI response is missing concepts."
            )

        if len(raw_concepts) != expected_count:
            raise RuntimeError(
                "Creative AI returned an unexpected concept count."
            )

        concepts: list[CreativeConcept] = []

        for item in raw_concepts:
            if not isinstance(item, dict):
                raise RuntimeError(
                    "Creative concept must be a JSON object."
                )

            required = (
                "name",
                "angle",
                "hook",
                "script",
                "cta",
                "visual_idea",
                "target_audience",
            )

            if any(key not in item for key in required):
                raise RuntimeError(
                    "Creative concept is missing required fields."
                )

            if not isinstance(item["script"], list):
                raise RuntimeError(
                    "Creative concept script must be a list."
                )

            concepts.append(
                CreativeConcept(
                    name=str(item["name"]),
                    angle=str(item["angle"]),
                    hook=str(item["hook"]),
                    script=[
                        str(line)
                        for line in item["script"]
                    ],
                    cta=str(item["cta"]),
                    visual_idea=str(item["visual_idea"]),
                    target_audience=str(
                        item["target_audience"]
                    ),
                )
            )

        return concepts
