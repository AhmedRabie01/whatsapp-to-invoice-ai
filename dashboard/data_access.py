from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import AutomationLog, Customer, DailyReport, Invoice, Message, Order, Product, Task


class DashboardDataAccess:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_dashboard_payload(self) -> dict[str, object]:
        return {
            "metrics": self.get_overview_metrics(),
            "messages": self.get_recent_messages(limit=20),
            "orders": self.get_recent_orders(limit=20),
            "documents": self.get_recent_documents(limit=20),
            "tasks": self.get_recent_tasks(limit=20),
            "products": self.get_products(limit=100),
            "reports": self.get_daily_reports(limit=20),
            "automation_logs": self.get_automation_logs(limit=20),
        }

    def get_overview_metrics(self) -> dict[str, object]:
        total_messages = self.db.query(func.count(Message.id)).scalar() or 0
        total_orders = self.db.query(func.count(Order.id)).scalar() or 0
        total_documents = self.db.query(func.count(Invoice.id)).scalar() or 0
        open_tasks = (
            self.db.query(func.count(Task.id))
            .filter(Task.status == "open")
            .scalar()
            or 0
        )
        total_revenue = self.db.query(func.sum(Invoice.total_amount)).scalar() or Decimal("0.00")

        return {
            "total_messages": total_messages,
            "total_orders": total_orders,
            "total_documents": total_documents,
            "open_tasks": open_tasks,
            "total_revenue": f"{Decimal(total_revenue):.2f}",
        }

    def get_recent_messages(self, limit: int = 10) -> list[dict[str, object]]:
        messages = (
            self.db.query(Message)
            .options(joinedload(Message.customer))
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": message.id,
                "customer": message.customer.full_name if message.customer else "Unassigned",
                "channel": message.channel,
                "intent": message.intent or "unknown",
                "confidence": round(message.confidence_score or 0.0, 2),
                "status": message.status,
                "created_at": message.created_at.strftime("%Y-%m-%d %H:%M"),
                "content": message.content,
            }
            for message in messages
        ]

    def get_recent_orders(self, limit: int = 10) -> list[dict[str, object]]:
        orders = (
            self.db.query(Order)
            .options(joinedload(Order.customer), joinedload(Order.invoice))
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": order.id,
                "customer": order.customer.full_name if order.customer else "Unknown",
                "status": order.status,
                "order_type": order.order_type,
                "requested_date": order.requested_date.strftime("%Y-%m-%d") if order.requested_date else "-",
                "total_amount": f"{Decimal(order.total_amount):.2f}",
                "document_type": order.invoice.document_type if order.invoice else "-",
                "document_number": order.invoice.invoice_number if order.invoice else "-",
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for order in orders
        ]

    def get_recent_documents(self, limit: int = 10) -> list[dict[str, object]]:
        documents = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.order).joinedload(Order.customer))
            .order_by(Invoice.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": document.id,
                "invoice_number": document.invoice_number,
                "document_type": document.document_type,
                "status": document.status,
                "customer": document.order.customer.full_name if document.order and document.order.customer else "Unknown",
                "total_amount": f"{Decimal(document.total_amount):.2f}",
                "issue_date": document.issue_date.strftime("%Y-%m-%d"),
            }
            for document in documents
        ]

    def get_recent_tasks(self, limit: int = 10) -> list[dict[str, object]]:
        tasks = (
            self.db.query(Task)
            .options(joinedload(Task.customer), joinedload(Task.order))
            .order_by(Task.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": task.id,
                "title": task.title,
                "task_type": task.task_type,
                "priority": task.priority,
                "status": task.status,
                "customer": task.customer.full_name if task.customer else "Unknown",
                "order_id": task.order_id or "-",
                "created_at": task.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for task in tasks
        ]

    def get_products(self, limit: int = 50) -> list[dict[str, object]]:
        products = (
            self.db.query(Product)
            .order_by(Product.category.asc(), Product.name.asc())
            .limit(limit)
            .all()
        )
        return [
            {
                "sku": product.sku,
                "name": product.name,
                "category": product.category or "-",
                "unit_price": f"{Decimal(product.unit_price):.2f}",
                "unit_type": product.unit_type,
                "is_active": product.is_active,
            }
            for product in products
        ]

    def get_daily_reports(self, limit: int = 10) -> list[dict[str, object]]:
        reports = (
            self.db.query(DailyReport)
            .order_by(DailyReport.report_date.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "report_date": report.report_date.isoformat(),
                "total_messages": report.total_messages,
                "total_orders": report.total_orders,
                "total_invoices": report.total_invoices,
                "total_revenue": f"{Decimal(report.total_revenue):.2f}",
                "sent_via": report.sent_via or "-",
            }
            for report in reports
        ]

    def get_automation_logs(self, limit: int = 10) -> list[dict[str, object]]:
        logs = (
            self.db.query(AutomationLog)
            .order_by(AutomationLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "event_type": log.event_type,
                "status": log.status,
                "target_system": log.target_system or "-",
                "created_at": log.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for log in logs
        ]
