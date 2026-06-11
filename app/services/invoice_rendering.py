from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models import Customer, Invoice, Order


class InvoiceRenderingService:
    def __init__(self) -> None:
        template_dir = Path(__file__).resolve().parents[1] / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, *, customer: Customer, order: Order, invoice: Invoice) -> str:
        template = self.environment.get_template("invoice.html")
        return template.render(
            customer=customer,
            order=order,
            invoice=invoice,
        )
