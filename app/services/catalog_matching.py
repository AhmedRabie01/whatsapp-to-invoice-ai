import re

from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.ai import ExtractedItem
from app.schemas.pricing import MatchedCatalogItem


class CatalogMatchingService:
    def __init__(self, db: Session) -> None:
        self.repository = ProductRepository(db)

    def match_items(
        self,
        extracted_items: list[ExtractedItem],
    ) -> tuple[list[MatchedCatalogItem], list[str]]:
        catalog = self.repository.list_active()
        matched_items: list[MatchedCatalogItem] = []
        unmatched_items: list[str] = []

        for extracted_item in extracted_items:
            best_product = None
            best_score = 0.0

            for product in catalog:
                score = self._score_match(extracted_item.name, product.name)
                if extracted_item.item_type == "service" and product.unit_type == "service":
                    score += 0.05
                if extracted_item.item_type == "product" and product.unit_type != "service":
                    score += 0.05

                if score > best_score:
                    best_score = score
                    best_product = product

            if best_product and best_score >= 0.45:
                matched_items.append(
                    MatchedCatalogItem(
                        product_id=best_product.id,
                        sku=best_product.sku,
                        name=best_product.name,
                        requested_name=extracted_item.name,
                        category=best_product.category,
                        quantity=extracted_item.quantity,
                        unit_type=best_product.unit_type,
                        unit_price=best_product.unit_price,
                        line_total=best_product.unit_price * extracted_item.quantity,
                        match_score=round(min(best_score, 0.99), 2),
                    )
                )
            else:
                unmatched_items.append(extracted_item.name)

        return matched_items, unmatched_items

    def _score_match(self, requested_name: str, catalog_name: str) -> float:
        requested_normalized = self._normalize(requested_name)
        catalog_normalized = self._normalize(catalog_name)

        if requested_normalized == catalog_normalized:
            return 0.95
        if requested_normalized in catalog_normalized or catalog_normalized in requested_normalized:
            return 0.82

        requested_tokens = set(requested_normalized.split())
        catalog_tokens = set(catalog_normalized.split())
        if not requested_tokens or not catalog_tokens:
            return 0.0

        overlap = len(requested_tokens & catalog_tokens)
        union = len(requested_tokens | catalog_tokens)
        return overlap / union

    def _normalize(self, text: str) -> str:
        text = text.casefold().replace("-", " ")
        text = re.sub(r"[^a-z0-9\u0600-\u06ff\s]", "", text)
        return re.sub(r"\s+", " ", text).strip()
