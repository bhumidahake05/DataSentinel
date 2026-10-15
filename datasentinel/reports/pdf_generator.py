"""PDF report generation for DataSentinel using ReportLab."""

from html import escape
from html.parser import HTMLParser
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer


class _ReportTextParser(HTMLParser):
    """Extract readable text from an HTML report."""

    BLOCK_TAGS = {
        "h1", "h2", "h3", "h4", "p", "div",
        "section", "article", "li", "tr", "header", "footer",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self.current: list[str] = []
        self.skip_depth = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag in {"script", "style"}:
            self.skip_depth += 1
            return

        if self.skip_depth:
            return

        if tag in self.BLOCK_TAGS or tag == "br":
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.skip_depth = max(0, self.skip_depth - 1)
            return

        if not self.skip_depth and tag in self.BLOCK_TAGS:
            self._flush()

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            text = " ".join(data.split())
            if text:
                self.current.append(text)

    def _flush(self) -> None:
        text = " ".join(self.current).strip()
        if text:
            self.blocks.append(text)
        self.current.clear()

    def finish(self) -> list[str]:
        """Return extracted text blocks."""
        self._flush()
        return self.blocks


class PDFReportGenerator:
    """Generate a PDF from a DataSentinel HTML report."""

    def generate_pdf(self, html_path: str, output_path: str) -> None:
        """Convert the report's readable text into a PDF."""
        source = Path(html_path)
        destination = Path(output_path)

        if not source.is_file():
            raise FileNotFoundError(
                f"HTML report was not found: {source}"
            )

        destination.parent.mkdir(parents=True, exist_ok=True)

        parser = _ReportTextParser()
        parser.feed(source.read_text(encoding="utf-8"))
        text_blocks = parser.finish()

        if not text_blocks:
            text_blocks = ["DataSentinel Quality Report"]

        styles = getSampleStyleSheet()
        styles["Title"].textColor = colors.HexColor("#17365D")
        styles["Heading2"].textColor = colors.HexColor("#24527A")

        document = SimpleDocTemplate(
            str(destination),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title="DataSentinel Quality Report",
        )

        story: list[Flowable] = []

        for index, block in enumerate(text_blocks):
            safe_text = escape(block)

            if index == 0:
                style = styles["Title"]
            elif len(block) < 80 and block.isupper():
                style = styles["Heading2"]
            else:
                style = styles["BodyText"]

            story.append(Paragraph(safe_text, style))
            story.append(Spacer(1, 5 * mm))

        document.build(story)
