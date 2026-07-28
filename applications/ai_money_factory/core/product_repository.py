from typing import List, Optional

from .opportunity_engine import Product, OpportunityEngine, Opportunity


class ProductRepository:

    def __init__(self):
        self._products: List[Product] = []
        self._engine = OpportunityEngine()

    def add(self, product: Product) -> None:
        self._products.append(product)

    def remove(self, name: str) -> bool:
        for product in self._products:
            if product.name == name:
                self._products.remove(product)
                return True
        return False

    def update(self, name: str, new_product: Product) -> bool:
        for index, product in enumerate(self._products):
            if product.name == name:
                self._products[index] = new_product
                return True
        return False

    def find(self, name: str) -> Optional[Product]:
        for product in self._products:
            if product.name == name:
                return product
        return None

    def all(self) -> List[Product]:
        return list(self._products)

    def ranked(self) -> List[Opportunity]:
        opportunities = [
            self._engine.calculate(product)
            for product in self._products
        ]

        opportunities.sort(
            key=lambda item: item.win_score,
            reverse=True,
        )

        return opportunities

    def top(self, limit: int = 10) -> List[Opportunity]:
        return self.ranked()[:limit]
