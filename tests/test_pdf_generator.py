from pathlib import Path

from datasentinel.reports.pdf_generator import PDFReportGenerator


def test_generate_pdf(tmp_path: Path) -> None:
    html_file = tmp_path / "report.html"
    pdf_file = tmp_path / "report.pdf"

    html_file.write_text(
        """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>DataSentinel Report</h1>
            <p>Test report</p>
        </body>
        </html>
        """,
        encoding="utf-8",
    )

    generator = PDFReportGenerator()

    generator.generate_pdf(
        str(html_file),
        str(pdf_file),
    )

    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0