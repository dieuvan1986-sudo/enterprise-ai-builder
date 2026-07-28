from __future__ import annotations

from applications.ai_money_factory.core.daily_opportunity_engine import (
    DailyMission,
)


class DailyBriefFormatter:
    """
    Convert a DailyMission into a Telegram-friendly business brief.
    """

    def format(self, mission: DailyMission) -> str:
        lines: list[str] = [
            "🔥 MÓN HAY 365 — DAILY MISSION",
            "",
            f"📊 Đã phân tích: {mission.total_products} sản phẩm",
            "",
        ]

        if not mission.top_products:
            lines.extend(
                [
                    "⚠️ Chưa có sản phẩm đủ dữ liệu.",
                    "",
                    "🔎 NEXT: Thu thập thêm tín hiệu thị trường.",
                ]
            )
            return "\n".join(lines)

        winner = mission.top_products[0]
        product = winner.product

        lines.extend(
            [
                "🥇 SẢN PHẨM ƯU TIÊN",
                f"📦 {product.name}",
                f"💰 Giá: {product.price:,.0f} VNĐ",
                f"⭐ Win Score: {winner.win_score}/10",
                f"🛡 Confidence: {winner.confidence}",
                f"🎯 Action: {winner.action}",
                "",
            ]
        )

        if winner.reasons:
            lines.append(
                "💡 Lý do: " + ", ".join(winner.reasons)
            )
            lines.append("")

        collect_more = [
            opportunity
            for opportunity in mission.top_products[1:]
            if opportunity.action == "COLLECT_MORE_DATA"
        ]

        if collect_more:
            lines.append("🔎 CẦN THU THẬP THÊM DỮ LIỆU")

            for opportunity in collect_more[:5]:
                lines.append(
                    f"• {opportunity.product.name} "
                    f"({opportunity.win_score}/10)"
                )

            lines.append("")

        lines.extend(
            [
                "🎬 NEXT",
                "Phân tích sản phẩm #1 → tạo concept → script → video AI.",
            ]
        )

        return "\n".join(lines)
