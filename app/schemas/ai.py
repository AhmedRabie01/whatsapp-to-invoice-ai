from pydantic import BaseModel, ConfigDict, Field


class MessageExtractionRequest(BaseModel):
    message_text: str = Field(min_length=1)
    channel: str = "whatsapp"
    customer_id: int | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class ExtractedItem(BaseModel):
    name: str
    quantity: int = 1
    item_type: str


class MessageExtractionResponse(BaseModel):
    provider_name: str
    original_message: str
    intent: str
    customer_need: str
    items_or_services: list[ExtractedItem] = Field(default_factory=list)
    location: str | None = None
    requested_date_text: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    confidence_score: float
    suggested_next_action: str
