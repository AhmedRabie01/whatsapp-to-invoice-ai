from pathlib import Path
import sys

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import SessionLocal, init_db
from dashboard.data_access import DashboardDataAccess


st.set_page_config(
    page_title="SME Workflow Dashboard",
    page_icon="IN",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_dashboard_data() -> dict[str, object]:
    init_db()
    db = SessionLocal()
    try:
        data_access = DashboardDataAccess(db)
        return {
            "metrics": data_access.get_overview_metrics(),
            "messages": data_access.get_recent_messages(),
            "orders": data_access.get_recent_orders(),
            "documents": data_access.get_recent_documents(),
            "tasks": data_access.get_recent_tasks(),
            "products": data_access.get_products(),
            "reports": data_access.get_daily_reports(),
            "automation_logs": data_access.get_automation_logs(),
        }
    finally:
        db.close()


def count_by(rows: list[dict[str, object]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, "Unknown"))
        counts[value] = counts.get(value, 0) + 1
    return counts


def apply_filters(
    rows: list[dict[str, object]],
    *,
    query: str = "",
    field: str | None = None,
    value: str = "All",
) -> list[dict[str, object]]:
    filtered = rows
    if field and value != "All":
        filtered = [row for row in filtered if str(row.get(field, "")) == value]

    if query:
        query_lower = query.casefold()
        filtered = [
            row
            for row in filtered
            if query_lower in " ".join(str(item).casefold() for item in row.values())
        ]

    return filtered


def render_metric_cards(metrics: dict[str, object]) -> None:
    columns = st.columns(5)
    metric_items = [
        ("Messages", metrics["total_messages"], "Captured from inbox and automation routes"),
        ("Orders", metrics["total_orders"], "Draft orders and quotations created"),
        ("Documents", metrics["total_documents"], "Invoices and quotations generated"),
        ("Open Tasks", metrics["open_tasks"], "Operational work still pending"),
        ("Revenue (AED)", metrics["total_revenue"], "Total document value tracked"),
    ]
    for column, (label, value, help_text) in zip(columns, metric_items):
        with column:
            st.metric(label, value)
            st.caption(help_text)


def render_stat_strip(title: str, counts: dict[str, int], empty_message: str) -> None:
    st.subheader(title)
    if not counts:
        st.info(empty_message)
        return

    columns = st.columns(max(len(counts), 1))
    for column, (label, value) in zip(columns, counts.items()):
        column.markdown(
            f"""
            <div class="mini-card">
                <div class="mini-label">{label}</div>
                <div class="mini-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_data_panel(
    *,
    title: str,
    rows: list[dict[str, object]],
    empty_message: str,
    filter_field: str | None = None,
    filter_label: str | None = None,
) -> None:
    st.subheader(title)
    if not rows:
        st.info(empty_message)
        return

    controls = st.columns([1.2, 1.2, 3])
    selected_value = "All"
    if filter_field:
        options = ["All"] + sorted({str(row.get(filter_field, "")) for row in rows if row.get(filter_field) is not None})
        selected_value = controls[0].selectbox(
            filter_label or f"Filter by {filter_field}",
            options,
            key=f"{title}-filter",
        )
    else:
        controls[0].markdown("")

    limit = controls[1].selectbox(
        "Rows",
        [5, 10, 20, 50],
        index=1,
        key=f"{title}-limit",
    )
    query = controls[2].text_input(
        "Search",
        placeholder="Search across all visible columns",
        key=f"{title}-search",
    )

    filtered_rows = apply_filters(
        rows,
        query=query,
        field=filter_field,
        value=selected_value,
    )

    st.caption(f"Showing {min(len(filtered_rows), limit)} of {len(filtered_rows)} matching rows")
    st.dataframe(filtered_rows[:limit], use_container_width=True, hide_index=True)


def render_command_center(data: dict[str, object]) -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <div>
                <div class="eyebrow">Operator Console</div>
                <h2>Command Center</h2>
                <p>Track the entire workflow from message intake to invoice generation, follow-up tasks, and automation dispatch.</p>
            </div>
            <div class="hero-chip-wrap">
                <span class="hero-chip">AI Intake</span>
                <span class="hero-chip">Commercial Workflow</span>
                <span class="hero-chip">Operations Follow-up</span>
                <span class="hero-chip">Automation Ready</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_metric_cards(data["metrics"])

    left, right = st.columns([1.4, 1])
    with left:
        render_stat_strip(
            "Message Intent Mix",
            count_by(data["messages"], "intent"),
            "No extracted messages yet.",
        )
        render_data_panel(
            title="Action Queue",
            rows=data["tasks"],
            empty_message="No tasks generated yet.",
            filter_field="priority",
            filter_label="Priority",
        )
    with right:
        render_stat_strip(
            "Document Types",
            count_by(data["documents"], "document_type"),
            "No commercial documents yet.",
        )
        st.subheader("Operator Checklist")
        st.markdown(
            """
            - Confirm all `high` priority tasks are assigned.
            - Review `manual_review` tasks before sending customer confirmations.
            - Track quotation approvals before converting service quotes into work orders.
            - Trigger the daily report after operational review is complete.
            """
        )

    st.subheader("Workflow Stages")
    stage_columns = st.columns(4)
    stages = [
        ("1. Intake", "Messages arrive and are classified by the AI extraction layer."),
        ("2. Commerce", "Products or services are matched and priced into draft documents."),
        ("3. Operations", "Follow-up tasks are generated for approvals and missing details."),
        ("4. Automation", "Daily reports and automation logs capture the end-of-day picture."),
    ]
    for column, (title, description) in zip(stage_columns, stages):
        column.markdown(
            f"""
            <div class="stage-card">
                <div class="stage-title">{title}</div>
                <div class="stage-body">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Quick Test Commands")
    st.code(
        """Invoke-RestMethod http://127.0.0.1:8000/orders/from-message -Method Post -ContentType 'application/json' -Body '{"message_text":"I need cleaning for a 2-bedroom apartment tomorrow in Dubai Marina. How much?","customer_name":"Sara Demo","customer_phone":"+971500000123"}'""",
        language="powershell",
    )
    st.code(
        """Invoke-RestMethod http://127.0.0.1:8000/automation/daily-report -Method Post -Headers @{ "x-webhook-secret" = "change-this-secret" } -ContentType 'application/json' -Body '{"send_email":false}'""",
        language="powershell",
    )


def render_workflow_story(data: dict[str, object]) -> None:
    render_data_panel(
        title="Inbox",
        rows=data["messages"],
        empty_message="No processed messages yet. Use /messages/extract or /orders/from-message to generate records.",
        filter_field="intent",
        filter_label="Intent",
    )
    render_data_panel(
        title="Orders",
        rows=data["orders"],
        empty_message="No orders available yet.",
        filter_field="order_type",
        filter_label="Order Type",
    )
    render_data_panel(
        title="Invoices / Quotations",
        rows=data["documents"],
        empty_message="No invoices or quotations available yet.",
        filter_field="document_type",
        filter_label="Document Type",
    )


def render_task_console(data: dict[str, object]) -> None:
    left, right = st.columns([1.5, 1])
    with left:
        render_data_panel(
            title="Operational Tasks",
            rows=data["tasks"],
            empty_message="No tasks generated yet.",
            filter_field="priority",
            filter_label="Priority",
        )
    with right:
        render_stat_strip(
            "Task Types",
            count_by(data["tasks"], "task_type"),
            "No task types available yet.",
        )
        render_stat_strip(
            "Task Status",
            count_by(data["tasks"], "status"),
            "No task statuses available yet.",
        )
        st.subheader("How To Use")
        st.markdown(
            """
            - Sort by `priority` to work the queue from high to low.
            - `manual_review` means staff should review AI or catalog output.
            - `quotation_follow_up` tracks customer confirmation work.
            - `service_coordination` tracks technician or schedule alignment.
            """
        )


def render_catalog_console(data: dict[str, object]) -> None:
    render_data_panel(
        title="Products / Services",
        rows=data["products"],
        empty_message="No products found. Product seeding should populate this automatically.",
        filter_field="category",
        filter_label="Category",
    )
    st.info(
        "This catalog is the bridge between AI extraction and commercial workflow. "
        "Task 4 uses it for matching and pricing."
    )


def render_automation_console(data: dict[str, object]) -> None:
    top_left, top_right = st.columns(2)
    with top_left:
        render_data_panel(
            title="Daily Reports",
            rows=data["reports"],
            empty_message="No daily reports yet. Trigger /reports/generate or /automation/daily-report.",
            filter_field="sent_via",
            filter_label="Sent Via",
        )
    with top_right:
        render_data_panel(
            title="Automation Logs",
            rows=data["automation_logs"],
            empty_message="No automation logs yet. Trigger the automation endpoint to populate this view.",
            filter_field="target_system",
            filter_label="Target System",
        )

    st.subheader("Automation Runbook")
    st.markdown(
        """
        1. Confirm operational tasks are in a good state.
        2. Generate the daily report from FastAPI or n8n.
        3. Review the report row in this dashboard.
        4. Verify a matching automation log was recorded.
        5. If email sending is enabled, confirm `sent_via` is populated.
        """
    )


def main() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(239, 188, 72, 0.18), transparent 28%),
                    linear-gradient(180deg, #f5f1e7 0%, #fffdf8 100%);
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f3526 0%, #1b5b41 55%, #236b53 100%);
            }
            [data-testid="stSidebar"] * {
                color: #f7f4ed;
            }
            .block-container {
                padding-top: 1.6rem;
                max-width: 1400px;
            }
            .hero-panel {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 20px;
                padding: 22px 24px;
                border-radius: 22px;
                background: linear-gradient(135deg, #163d2f 0%, #245a43 62%, #e5b54d 160%);
                color: #fff9ec;
                margin-bottom: 18px;
                box-shadow: 0 18px 32px rgba(20, 44, 35, 0.15);
            }
            .hero-panel h2 {
                margin: 0 0 6px 0;
                font-size: 2rem;
            }
            .hero-panel p {
                margin: 0;
                max-width: 700px;
                color: rgba(255, 249, 236, 0.85);
            }
            .eyebrow {
                text-transform: uppercase;
                letter-spacing: 0.16em;
                font-size: 0.78rem;
                opacity: 0.85;
                margin-bottom: 8px;
            }
            .hero-chip-wrap {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                justify-content: flex-end;
            }
            .hero-chip {
                padding: 8px 12px;
                border-radius: 999px;
                background: rgba(255, 249, 236, 0.14);
                border: 1px solid rgba(255, 249, 236, 0.18);
                font-size: 0.88rem;
            }
            .mini-card {
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.72);
                padding: 14px 16px;
                border: 1px solid rgba(16, 53, 38, 0.08);
                box-shadow: 0 8px 20px rgba(34, 51, 43, 0.05);
            }
            .mini-label {
                color: #4e5c56;
                font-size: 0.84rem;
                margin-bottom: 4px;
            }
            .mini-value {
                color: #103526;
                font-size: 1.6rem;
                font-weight: 700;
            }
            .stage-card {
                border-radius: 20px;
                min-height: 150px;
                background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(247,243,234,0.96) 100%);
                padding: 18px;
                border: 1px solid rgba(16, 53, 38, 0.08);
                box-shadow: 0 10px 24px rgba(34, 51, 43, 0.06);
            }
            .stage-title {
                font-weight: 700;
                font-size: 1.05rem;
                color: #133d2d;
                margin-bottom: 8px;
            }
            .stage-body {
                color: #4f5f58;
                line-height: 1.5;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("WhatsApp-to-Invoice AI Workflow Dashboard")
    st.caption("Operator-facing workspace for AI intake, commercial workflow, follow-up tasks, and automation control.")

    data = load_dashboard_data()
    st.sidebar.markdown("## Control Surface")
    st.sidebar.caption("Use this panel to move between operational views.")
    st.sidebar.metric("Open Tasks", data["metrics"]["open_tasks"])
    st.sidebar.metric("Revenue (AED)", data["metrics"]["total_revenue"])
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Suggested Flow")
    st.sidebar.markdown(
        """
        1. Review new inbox items
        2. Check commercial documents
        3. Resolve high-priority tasks
        4. Trigger daily automation
        """
    )

    pages = {
        "Command Center": lambda: render_command_center(data),
        "Workflow Browser": lambda: render_workflow_story(data),
        "Task Console": lambda: render_task_console(data),
        "Catalog": lambda: render_catalog_console(data),
        "Reports & Automation": lambda: render_automation_console(data),
    }

    selected_page = st.sidebar.radio("Navigate", list(pages.keys()))
    pages[selected_page]()


if __name__ == "__main__":
    main()
