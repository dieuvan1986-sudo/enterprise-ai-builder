from applications.ai_money_factory.collectors.shopee_collector import (
    ShopeeProductSignal,
)
from applications.ai_money_factory.core.opportunity_engine import (
    OpportunityEngine,
)
from applications.ai_money_factory.core.shopee_signal_mapper import (
    ShopeeSignalMapper,
)


signal = ShopeeProductSignal(
    name="Xot Pho Mai Tanzy Foods 500g",
    category="Bach Hoa Online",
    price=64_000,
    commission_rate=16.5,
    sold_count=200_000,
    sales_growth_7d=28_600,
    rating=4.9,
    creator_count=8_500,
)

mapper = ShopeeSignalMapper()
product = mapper.map(signal)

engine = OpportunityEngine()
opportunity = engine.calculate(product)

print("=== AI MONEY FACTORY ===")
print(f"Product: {product.name}")
print(f"Price: {product.price:,.0f} VND")
print()
print("Signals:")
print(f"  Trend:       {product.trend_score}/10")
print(f"  Demand:      {product.demand_score}/10")
print(f"  Commission:  {product.commission}/10")
print(f"  Video:       {product.video_score}/10")
print(f"  Competition: {product.competition_score}/10")
print()
print(f"WIN SCORE: {opportunity.win_score}/10")
print(f"Priority:  {opportunity.priority}")
print(f"Action:    {opportunity.action}")
print(f"Reasons:   {', '.join(opportunity.reasons)}")
