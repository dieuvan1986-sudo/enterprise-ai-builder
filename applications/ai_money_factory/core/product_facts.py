from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ProductFacts:
    """
    Verified product information.

    This model is the single source of truth for everything
    the Creative Engine is allowed to mention or visually depict.

    Every field should originate from a trusted source
    (Shopee product page, official brand page, seller information,
    official product imagery, or another approved data source).
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    product_id: str
    name: str

    brand: str | None = None
    category: str | None = None
    sku: str | None = None

    # ------------------------------------------------------------------
    # Packaging
    # ------------------------------------------------------------------

    weight: str | None = None
    size: str | None = None
    unit: str | None = None

    # ------------------------------------------------------------------
    # Verified content
    # ------------------------------------------------------------------

    description: str | None = None

    # Consumer-facing factual claims verified from approved sources.
    verified_facts: list[str] = field(default_factory=list)

    # Visual uses or appearances explicitly supported by approved
    # product imagery or other verified evidence.
    verified_visual_facts: list[str] = field(default_factory=list)

    ingredients: list[str] = field(default_factory=list)

    usage: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Commercial information
    # ------------------------------------------------------------------

    price: float | None = None

    currency: str = "VND"

    price_verified: bool = False

    affiliate_url: str | None = None

    image_urls: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    source: str | None = None

    source_url: str | None = None

    verified_at: datetime | None = None

    confidence: float = 1.0
