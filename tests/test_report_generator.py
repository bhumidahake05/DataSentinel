from pathlib import Path

from datasentinel.reports.generator import ReportGenerator


def test_generate_html_report(tmp_path: Path) -> None:
    output = tmp_path / "report.html"

    report_data = {
        "title": "DataSentinel Quality Report",
        "summary": "Test quality report",
        "total_rules": 2,
        "passed_rules": 1,
        "failed_rules": 1,
        "total_anomalies": 2,
        "rule_results": [
            {
                "rule_type": "null_check",
                "column": "name",
                "passed": True,
                "violations": 0,
                "message": "No null values found.",
            },
            {
                "rule_type": "unique_check",
                "column": "id",
                "passed": False,
                "violations": 1,
                "message": "Duplicate value found.",
            },
        ],
        "pass_rate_labels": ["null_check", "unique_check"],
        "pass_rate_values": [100, 0],
        "anomaly_labels": ["Run 1", "Run 2"],
        "anomaly_values": [1, 2],
    }

    generator = ReportGenerator()
    generator.generate_html(str(output), report_data)

    assert output.exists()

    content = output.read_text(encoding="utf-8")

    assert "DataSentinel Quality Report" in content
    assert "Rule Pass Rate" in content
    assert "Anomaly Trend" in content