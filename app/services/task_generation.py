from dataclasses import dataclass

from app.models import Customer
from app.repositories.task_repository import TaskRepository
from app.schemas.ai import MessageExtractionResponse
from app.schemas.pricing import MatchedCatalogItem
from app.services.scenario_profiles import resolve_scenario


@dataclass
class TaskDraft:
    task_type: str
    title: str
    description: str
    priority: str = "medium"


class TaskGenerationService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def generate_tasks(
        self,
        *,
        customer: Customer,
        order_id: int,
        message_id: int,
        extraction: MessageExtractionResponse,
        matched_items: list[MatchedCatalogItem],
        unmatched_items: list[str],
        document_type: str,
        has_customer_phone: bool,
    ):
        task_drafts = self._common_task_drafts(
            extraction=extraction,
            unmatched_items=unmatched_items,
            document_type=document_type,
            has_customer_phone=has_customer_phone,
        )
        scenario = resolve_scenario(extraction, matched_items)
        task_drafts.extend(
            self._scenario_task_drafts(
                scenario=scenario,
                extraction=extraction,
            )
        )

        unique_drafts = self._deduplicate(task_drafts)
        generated_tasks = []

        for draft in unique_drafts:
            generated_tasks.append(
                self.repository.create_task(
                    customer_id=customer.id,
                    order_id=order_id,
                    message_id=message_id,
                    task_type=draft.task_type,
                    title=draft.title,
                    description=draft.description,
                    priority=draft.priority,
                )
            )

        return generated_tasks

    def _common_task_drafts(
        self,
        *,
        extraction: MessageExtractionResponse,
        unmatched_items: list[str],
        document_type: str,
        has_customer_phone: bool,
    ) -> list[TaskDraft]:
        drafts: list[TaskDraft] = []

        if not has_customer_phone:
            drafts.append(
                TaskDraft(
                    task_type="missing_contact",
                    title="Collect customer phone number",
                    description="Customer record has no phone number. Collect a reachable contact number for follow-up.",
                    priority="high",
                )
            )

        if unmatched_items:
            drafts.append(
                TaskDraft(
                    task_type="manual_review",
                    title="Review unmatched catalog items",
                    description=(
                        "The following extracted items did not match the catalog: "
                        + ", ".join(unmatched_items)
                        + "."
                    ),
                    priority="high",
                )
            )

        if extraction.confidence_score < 0.70:
            drafts.append(
                TaskDraft(
                    task_type="manual_review",
                    title="Review low-confidence extraction",
                    description="AI extraction confidence is low. Review the message manually before processing further.",
                    priority="high",
                )
            )

        if document_type == "quotation":
            drafts.append(
                TaskDraft(
                    task_type="quotation_follow_up",
                    title="Follow up on quotation approval",
                    description="A quotation was generated and should be followed up with the customer for approval.",
                    priority="medium",
                )
            )

        if extraction.missing_information:
            drafts.append(
                TaskDraft(
                    task_type="customer_follow_up",
                    title="Send customer follow-up reply",
                    description=(
                        "Contact the customer to collect the missing information: "
                        + ", ".join(extraction.missing_information)
                        + "."
                    ),
                    priority="medium",
                )
            )

        return drafts

    def _scenario_task_drafts(
        self,
        *,
        scenario: str,
        extraction: MessageExtractionResponse,
    ) -> list[TaskDraft]:
        missing = set(extraction.missing_information)
        drafts: list[TaskDraft] = []

        if scenario == "pharmacy":
            if "delivery location" in missing:
                drafts.append(
                    TaskDraft(
                        task_type="missing_information",
                        title="Collect delivery location",
                        description="The order requires a delivery location before fulfillment can proceed.",
                        priority="high",
                    )
                )
            if "delivery date" in missing:
                drafts.append(
                    TaskDraft(
                        task_type="missing_information",
                        title="Collect delivery date",
                        description="The order requires a delivery date before scheduling dispatch.",
                        priority="medium",
                    )
                )

        if scenario == "cleaning":
            if "service location" in missing:
                drafts.append(
                    TaskDraft(
                        task_type="missing_information",
                        title="Collect service location",
                        description="Cleaning service location is missing and must be confirmed before quoting accurately.",
                        priority="high",
                    )
                )
            if "service date" in missing:
                drafts.append(
                    TaskDraft(
                        task_type="missing_information",
                        title="Collect service date",
                        description="Cleaning service date is missing and must be confirmed before scheduling.",
                        priority="high",
                    )
                )

        if scenario == "maintenance":
            drafts.append(
                TaskDraft(
                    task_type="service_coordination",
                    title="Confirm technician availability",
                    description="A maintenance request was created. Confirm technician availability before customer confirmation.",
                    priority="high",
                )
            )
            if extraction.requested_date_text:
                drafts.append(
                    TaskDraft(
                        task_type="service_coordination",
                        title="Confirm appointment schedule",
                        description="Confirm the requested maintenance date and time window with the customer.",
                        priority="medium",
                    )
                )
            if "service location" in missing:
                drafts.append(
                    TaskDraft(
                        task_type="missing_information",
                        title="Collect service location",
                        description="Maintenance visit location is missing and must be confirmed before dispatch.",
                        priority="high",
                    )
                )

        return drafts

    def _deduplicate(self, drafts: list[TaskDraft]) -> list[TaskDraft]:
        seen: set[tuple[str, str]] = set()
        unique: list[TaskDraft] = []

        for draft in drafts:
            key = (draft.task_type, draft.title)
            if key in seen:
                continue
            seen.add(key)
            unique.append(draft)

        return unique
