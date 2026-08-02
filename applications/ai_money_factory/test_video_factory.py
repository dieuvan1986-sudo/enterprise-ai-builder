from applications.ai_money_factory.core.creative_engine import (
    CreativeConcept,
)
from applications.ai_money_factory.core.video_factory import (
    VideoFactory,
)


concept = CreativeConcept(
    name="Bàn Ăn Có Điểm Nhấn",
    angle=(
        "Tình huống món ăn quen thuộc được làm nổi bật "
        "bằng thao tác chấm/rưới trực quan"
    ),
    hook="Cùng một đĩa đồ ăn, chỉ đổi góc nhìn này.",
    script=[
        (
            "Đặt món ăn ở giữa khung hình, "
            "xốt phô mai Tanzy Foods 500g xuất hiện cạnh bên."
        ),
        (
            "Rưới một đường xốt lên phần ăn "
            "rồi chuyển sang cảnh chấm cận tay."
        ),
        (
            "Video giữ trọng tâm vào chuyển động rưới, "
            "chấm và nhận diện sản phẩm."
        ),
    ],
    cta="Xem sản phẩm trong giỏ nếu bạn muốn tìm hiểu thêm.",
    visual_idea=(
        "Mở đầu top-down với món ăn và chuyển động rưới xốt. "
        "Chuyển sang góc 45 độ với cảnh chấm cận tay. "
        "Dùng macro để thể hiện chuyển động của xốt. "
        "Bao bì Xot Pho Mai Tanzy Foods 500g xuất hiện rõ "
        "trong bố cục, nhãn hướng về camera. "
        "Kết thúc bằng món ăn, chén xốt và sản phẩm trong "
        "một khung hình sạch. Không hiển thị giá."
    ),
    target_audience=(
        "Người thích video đồ ăn trực quan "
        "và mua sản phẩm bách hóa online"
    ),
)

factory = VideoFactory()
package = factory.build(concept)

print("=== MON HAY 365 - AI VIDEO PACKAGE ===")
print(f"Title: {package.title}")
print(f"Format: {package.format}")
print(f"Style: {package.production_style}")
print(f"Duration: {package.total_duration_seconds}s")
print(f"Hook: {package.hook}")
print(f"CTA: {package.cta}")
print()

for scene in package.scenes:
    print("=" * 60)
    print(
        f"SCENE {scene.scene_number} "
        f"- {scene.purpose} "
        f"- {scene.duration_seconds}s"
    )
    print("=" * 60)

    print(f"Narration: {scene.narration}")

    if scene.text_overlay:
        print(f"Overlay: {scene.text_overlay}")

    print(f"Visual prompt: {scene.visual_prompt}")
    print()

print("=" * 60)

if (
    len(package.scenes) == 5
    and package.total_duration_seconds == 25
    and package.format == "9:16"
):
    print("STATUS: READY_FOR_AI_VIDEO")
else:
    print("STATUS: VIDEO_PACKAGE_REVIEW_REQUIRED")
