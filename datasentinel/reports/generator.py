from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class ReportGenerator:
    """Generate HTML quality reports using Jinja2."""

    def __init__(self, template_directory: str = "datasentinel/templates") -> None:
        self.template_directory = Path(template_directory)
        self.environment = Environment(
            loader=FileSystemLoader(self.template_directory)
        )

    def generate_html(
        self,
        output_path: str,
        report_data: dict[str, Any],
    ) -> None:
        """Generate an HTML report."""
        template = self.environment.get_template("report.html")
        html = template.render(**report_data)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html, encoding="utf-8")