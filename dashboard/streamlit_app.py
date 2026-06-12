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


def render_metric_cards(metrics: dict[str, object]) -> None:
    columns = st.columns(5)
    metric_items = [
        ("Messages", metrics["total_messages"]),
        ("Orders", metrics["total_orders"]),
        ("Documents", metrics["total_documents"]),
        ("Open Tasks", metrics["open_tasks"]),
        ("Revenue (AED)", metrics["total_revenue"]),
    ]
    for column, (label, value) in zip(columns, metric_items):
        column.metric(label, value)


def render_table_section(title: str, rows: list[dict[str, object]], empty_message: str) -> None:
    st.subheader(title)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info(empty_message)


def render_overview(data: dict[str, object]) -> None:
    st.header("Operational Overview")
    render_metric_cards(data["metrics"])

    left, right = st.columns(2)
    with left:
        render_table_section(
            "Recent Messages",
            data["messages"][:5],
            "No processed messages yet. Run the workflow endpoint to populate the inbox.",
        )
    with right:
        render_table_section(
            "Recent Tasks",
            data["tasks"][:5],
            "No operational tasks yet. Task automation appears here after a workflow runs.",
        )

    render_table_section(
        "Recent Orders",
        data["orders"][:5],
        "No orders or quotations have been created yet.",
    )


def main() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(180deg, #f7f4ed 0%, #fffdf8 100%);
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #103d2b 0%, #1d5b43 100%);
            }
            [data-testid="stSidebar"] * {
                color: #f7f4ed;
            }
            .block-container {
                padding-top: 2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("WhatsApp-to-Invoice AI Workflow Dashboard")
    st.caption("Portfolio demo surface for message processing, commercial workflow, and operational follow-up.")

    data = load_dashboard_data()

    pages = {
        "Overview": lambda: render_overview(data),
        "Inbox": lambda: render_table_section(
            "Inbox",
            data["messages"],
            "No processed messages yet. Use /messages/extract or /orders/from-message to generate records.",
        ),
        "Orders": lambda: render_table_section(
            "Orders",
            data["orders"],
            "No orders available yet.",
        ),
        "Invoices / Quotations": lambda: render_table_section(
            "Invoices / Quotations",
            data["documents"],
            "No invoices or quotations available yet.",
        ),
        "Tasks": lambda: render_table_section(
            "Tasks",
            data["tasks"],
            "No tasks generated yet.",
        ),
        "Products / Services": lambda: render_table_section(
            "Products / Services",
            data["products"],
            "No products found. Product seeding should populate this automatically.",
        ),
        "Daily Reports": lambda: render_table_section(
            "Daily Reports",
            data["reports"],
            "Daily report generation will be added in Task 7.",
        ),
        "Automation Logs": lambda: render_table_section(
            "Automation Logs",
            data["automation_logs"],
            "Automation log activity will appear after Task 7 integrations are implemented.",
        ),
    }

    selected_page = st.sidebar.radio("Navigate", list(pages.keys()))
    pages[selected_page]()


if __name__ == "__main__":
    main()
