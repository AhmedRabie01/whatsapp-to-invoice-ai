import re

from app.ai.providers.base import AIProvider
from app.schemas.ai import ExtractedItem, MessageExtractionRequest, MessageExtractionResponse


class MockAIProvider(AIProvider):
    provider_name = "mock"

    def extract_message_data(
        self, request: MessageExtractionRequest
    ) -> MessageExtractionResponse:
        normalized_text = self._normalize_text(request.message_text)
        intent = self._detect_intent(normalized_text)
        items = self._extract_items(normalized_text, intent)
        location = self._extract_location(normalized_text)
        requested_date_text = self._extract_requested_date(normalized_text)
        missing_information = self._detect_missing_information(
            normalized_text=normalized_text,
            intent=intent,
            items=items,
            location=location,
            requested_date_text=requested_date_text,
        )
        customer_need = self._build_customer_need(intent, items, location)
        confidence_score = self._calculate_confidence(
            intent=intent,
            items=items,
            location=location,
            requested_date_text=requested_date_text,
            missing_information=missing_information,
        )
        suggested_next_action = self._suggest_next_action(intent, missing_information)

        return MessageExtractionResponse(
            provider_name=self.provider_name,
            original_message=request.message_text,
            intent=intent,
            customer_need=customer_need,
            items_or_services=items,
            location=location,
            requested_date_text=requested_date_text,
            missing_information=missing_information,
            confidence_score=confidence_score,
            suggested_next_action=suggested_next_action,
        )

    def _normalize_text(self, text: str) -> str:
        arabic_digits = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
        normalized = text.casefold().translate(arabic_digits)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _detect_intent(self, text: str) -> str:
        if any(keyword in text for keyword in ["panadol", "vitamin c", "فيتامين سي", "بانادول", "توصيل"]):
            return "product_order"
        if any(keyword in text for keyword in ["cleaning", "clean", "apartment", "quote", "quotation"]):
            return "service_quote"
        if any(keyword in text for keyword in ["ac not working", "maintenance", "repair", "technician", "ac "]):
            return "maintenance_request"
        return "general_inquiry"

    def _extract_items(self, text: str, intent: str) -> list[ExtractedItem]:
        items: list[ExtractedItem] = []

        if "panadol" in text or "بانادول" in text:
            items.append(
                ExtractedItem(
                    name="Panadol 500mg",
                    quantity=self._find_quantity(text, ["panadol", "بانادول"]),
                    item_type="product",
                )
            )
        if "vitamin c" in text or "فيتامين سي" in text:
            items.append(
                ExtractedItem(
                    name="Vitamin C 1000mg",
                    quantity=self._find_quantity(text, ["vitamin c", "فيتامين سي"]),
                    item_type="product",
                )
            )
        if intent == "service_quote":
            bedroom_count = self._extract_bedroom_count(text)
            service_name = "Apartment cleaning service"
            if bedroom_count:
                service_name = f"{bedroom_count}-bedroom apartment cleaning"
            items.append(
                ExtractedItem(
                    name=service_name,
                    quantity=1,
                    item_type="service",
                )
            )
        if intent == "maintenance_request":
            items.append(
                ExtractedItem(
                    name="AC diagnostic visit",
                    quantity=1,
                    item_type="service",
                )
            )

        return items

    def _find_quantity(self, text: str, aliases: list[str]) -> int:
        for alias in aliases:
            pattern = rf"(\d+)\s+{re.escape(alias)}"
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return 1

    def _extract_bedroom_count(self, text: str) -> int | None:
        match = re.search(r"(\d+)[-\s]?bedroom", text)
        if match:
            return int(match.group(1))
        return None

    def _extract_location(self, text: str) -> str | None:
        known_locations = [
            ("dubai marina", "Dubai Marina"),
            ("للعين", "Al Ain"),
            ("al ain", "Al Ain"),
            ("العين", "Al Ain"),
            ("abu dhabi", "Abu Dhabi"),
            ("dubai", "Dubai"),
        ]
        for needle, label in known_locations:
            if needle in text:
                return label
        return None

    def _extract_requested_date(self, text: str) -> str | None:
        if "tomorrow" in text or "بكرة" in text:
            return "tomorrow"
        if "today" in text or "اليوم" in text:
            return "today"
        return None

    def _detect_missing_information(
        self,
        normalized_text: str,
        intent: str,
        items: list[ExtractedItem],
        location: str | None,
        requested_date_text: str | None,
    ) -> list[str]:
        missing_information: list[str] = []

        if not items and intent != "general_inquiry":
            missing_information.append("requested item or service details")

        if intent == "product_order":
            if "delivery" in normalized_text or "توصيل" in normalized_text:
                if not location:
                    missing_information.append("delivery location")
                if not requested_date_text:
                    missing_information.append("delivery date")

        if intent in {"service_quote", "maintenance_request"}:
            if not location:
                missing_information.append("service location")
            if not requested_date_text:
                missing_information.append("service date")

        return missing_information

    def _build_customer_need(
        self,
        intent: str,
        items: list[ExtractedItem],
        location: str | None,
    ) -> str:
        if intent == "product_order" and items:
            product_names = ", ".join(item.name for item in items)
            location_text = f" to {location}" if location else ""
            return f"Customer wants product delivery for {product_names}{location_text}."
        if intent == "service_quote" and items:
            location_text = f" in {location}" if location else ""
            return f"Customer wants a cleaning quotation for {items[0].name}{location_text}."
        if intent == "maintenance_request" and items:
            location_text = f" in {location}" if location else ""
            return f"Customer needs a maintenance visit for {items[0].name}{location_text}."
        return "Customer message needs manual review."

    def _calculate_confidence(
        self,
        intent: str,
        items: list[ExtractedItem],
        location: str | None,
        requested_date_text: str | None,
        missing_information: list[str],
    ) -> float:
        score = 0.55 if intent == "general_inquiry" else 0.70
        if items:
            score += 0.10
        if location:
            score += 0.08
        if requested_date_text:
            score += 0.07
        if missing_information:
            score -= 0.08
        return round(max(0.35, min(score, 0.98)), 2)

    def _suggest_next_action(self, intent: str, missing_information: list[str]) -> str:
        if missing_information:
            joined_fields = ", ".join(missing_information)
            return f"Ask the customer to confirm: {joined_fields}."
        if intent == "product_order":
            return "Match catalog products and prepare a quotation or invoice draft."
        if intent == "service_quote":
            return "Prepare a service quotation and confirm the schedule."
        if intent == "maintenance_request":
            return "Create a maintenance task and confirm technician availability."
        return "Review the message manually and classify it."
