from applications.ai_money_factory.collectors.product_fact_collector import ProductFactCollector


collector = ProductFactCollector()

facts = collector.collect(
    product_id="tanzy-001",
    name="Xot Pho Mai Tanzy Foods 500g",
    brand="Tanzy Foods",
    category="Bách Hóa Online",
    weight="500g",
    verified_facts=[
        "Tên sản phẩm: Xot Pho Mai Tanzy Foods 500g",
        "Khối lượng: 500g",
    ],
    source="Shopee",
)

print("=== PRODUCT FACTS ===")
print(facts)
print()
print("Verified facts:")
for fact in facts.verified_facts:
    print("-", fact)
