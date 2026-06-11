from app.schemas.ai import MessageExtractionResponse
from app.schemas.pricing import MatchedCatalogItem


def resolve_scenario(
    extraction: MessageExtractionResponse,
    matched_items: list[MatchedCatalogItem],
) -> str:
    categories = {item.category for item in matched_items if item.category}

    if "pharmacy" in categories:
        return "pharmacy"
    if "cleaning" in categories:
        return "cleaning"
    if "maintenance" in categories or extraction.intent == "maintenance_request":
        return "maintenance"
    if extraction.intent == "service_quote":
        return "cleaning"
    if extraction.intent == "product_order":
        return "pharmacy"
    return "general"
