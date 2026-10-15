
"""Command-line interface for DataSentinel."""

import os
import smtplib
from datetime import datetime, timezone
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.table import Table

from datasentinel.alerts.service import AlertService
from datasentinel.connectors.dataset import DataSet
from datasentinel.connectors.registry import ConnectorRegistry
from datasentinel.reports.generator import ReportGenerator
from datasentinel.reports.pdf_generator import PDFReportGenerator
from datasentinel.rules.engine import RuleEngine, RuleResult
from datasentinel.rules.loader import load_rule_config
from datasentinel.rules.models import RuleConfig
from datasentinel.scheduler.runner import run_scheduler

app = typer.Typer(
    name="datasentinel",
    help="DataSentinel - Automated Data Quality & Pipeline Monitoring Platform",
)

console = Console()


def _get_connector_name(source: str) -> str:
    """Determine the connector type from a path, URL, or database URI."""
    normalized_source = source.lower()

    if normalized_source.startswith("sqlite://"):
        return "sqlite"

    if normalized_source.startswith(
        ("postgresql://", "postgresql+")
    ):
        return "postgresql"

    if normalized_source.startswith(("http://", "https://")):
        return "rest"

    suffix = Path(source).suffix.lower()

    if suffix == ".csv":
        return "csv"

    if suffix in {".xlsx", ".xls"}:
        return "excel"

    if suffix == ".json":
        return "json"

    if suffix in {".db", ".sqlite", ".sqlite3"}:
        return "sqlite"

    raise ValueError(
        f"Cannot determine connector type for source: {source}"
    )


def _execute_validation(
    config_path: str,
) -> tuple[RuleConfig, DataSet, list[RuleResult]]:
    """Load the configuration and execute all quality rules."""
    config = load_rule_config(config_path)

    connector_name = _get_connector_name(config.source)
    connector = ConnectorRegistry().get(connector_name)
    dataset = connector.connect(config.source)

    engine = RuleEngine()
    results: list[RuleResult] = [
        engine.run_rule(dataset, rule)
        for rule in config.rules
    ]

    return config, dataset, results


def _display_results(
    title: str,
    dataset: DataSet,
    results: list[RuleResult],
) -> tuple[int, int]:
    """Display rule results and return passed and failed counts."""
    table = Table(title=title)
    table.add_column("Rule")
    table.add_column("Column")
    table.add_column("Status")
    table.add_column("Violations", justify="right")
    table.add_column("Message")

    for result in results:
        status = (
            "[green]PASS[/green]"
            if result.passed
            else "[red]FAIL[/red]"
        )
        table.add_row(
            result.rule_type,
            result.column,
            status,
            str(result.violations),
            result.message,
        )

    console.print(table)

    passed_count = sum(
        1 for result in results if result.passed
    )
    failed_count = len(results) - passed_count

    console.print(f"Dataset rows: {len(dataset.data)}")
    console.print(f"Rules passed: {passed_count}")
    console.print(f"Rules failed: {failed_count}")

    return passed_count, failed_count


def _build_failure_summary(
    dataset_name: str,
    results: list[RuleResult],
) -> str:
    """Build a notification message for failed quality rules."""
    failed_results = [
        result for result in results if not result.passed
    ]

    lines = [
        f"DataSentinel quality alert: {dataset_name}",
        f"Failed rules: {len(failed_results)}",
        "",
    ]

    for result in failed_results:
        lines.append(
            f"- {result.rule_type} on column '{result.column}': "
            f"{result.violations} violation(s). {result.message}"
        )

    return "\n".join(lines)


def _send_failure_alert(summary: str) -> None:
    """Send configured email and Slack alerts."""
    alert_service = AlertService()
    recipient = os.getenv("DATASENTINEL_ALERT_RECIPIENT")

    if recipient and os.getenv("DATASENTINEL_SMTP_HOST"):
        try:
            alert_service.send_email(
                subject="DataSentinel: Data Quality Failure",
                summary=summary,
                recipient=recipient,
            )
            console.print("[green]Email alert sent.[/green]")
        except (
            ValueError,
            OSError,
            smtplib.SMTPException,
        ) as error:
            console.print(
                f"[yellow]Email alert failed: {error}[/yellow]"
            )

    if os.getenv("DATASENTINEL_SLACK_WEBHOOK"):
        try:
            alert_service.send_slack(summary)
            console.print("[green]Slack alert sent.[/green]")
        except (
            ValueError,
            OSError,
            httpx.HTTPError,
        ) as error:
            console.print(
                f"[yellow]Slack alert failed: {error}[/yellow]"
            )


def _run_validation(config_path: str) -> bool:
    """Run validation and notify configured channels on failure."""
    try:
        config, dataset, results = _execute_validation(config_path)
        _, failed_count = _display_results(
            config.name,
            dataset,
            results,
        )

        if failed_count:
            _send_failure_alert(
                _build_failure_summary(config.name, results)
            )

        return failed_count == 0

    except Exception as error:
        console.print(
            f"[bold red]Validation error:[/bold red] {error}"
        )
        return False


@app.command()
def validate(
    config: str = typer.Option(
        "datasentinel/rules/sample.yaml",
        "--config",
        "-c",
        help="Path to the YAML validation configuration.",
    ),
) -> None:
    """Validate a dataset using configured quality rules."""
    if not _run_validation(config):
        raise typer.Exit(code=1)


@app.command()
def report(
    config: str = typer.Option(
        "datasentinel/rules/sample.yaml",
        "--config",
        "-c",
        help="Path to the YAML validation configuration.",
    ),
    output_dir: str = typer.Option(
        "reports",
        "--output-dir",
        "-o",
        help="Directory for generated reports.",
    ),
) -> None:
    """Generate HTML and PDF quality reports."""
    try:
        rule_config, dataset, results = _execute_validation(config)
        passed, failed = _display_results(
            rule_config.name,
            dataset,
            results,
        )

        pass_rate = (
            round(passed / len(results) * 100, 2)
            if results
            else 100.0
        )

        if failed:
            _send_failure_alert(
                _build_failure_summary(rule_config.name, results)
            )

        report_data = {
            "title": "DataSentinel Quality Report",
            "dataset_name": rule_config.name,
            "generated_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M UTC"
            ),
            "total_rows": len(dataset.data),
            "total_rules": len(results),
            "passed_rules": passed,
            "failed_rules": failed,
            "pass_rate": pass_rate,
            "summary": f"{passed} rules passed and {failed} rules failed.",
            "results": [
                {
                    "rule_type": result.rule_type,
                    "column": result.column,
                    "passed": result.passed,
                    "violations": result.violations,
                    "message": result.message,
                }
                for result in results
            ],
            "anomaly_trend": [],
        }

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        html_path = output_path / "quality_report.html"
        pdf_path = output_path / "quality_report.pdf"

        ReportGenerator().generate_html(
            str(html_path),
            report_data,
        )
        PDFReportGenerator().generate_pdf(
            str(html_path),
            str(pdf_path),
        )

        console.print("[green]Reports generated successfully.[/green]")
        console.print(f"HTML report: {html_path}")
        console.print(f"PDF report: {pdf_path}")
        console.print(f"Pass rate: {pass_rate}%")

    except Exception as error:
        console.print(
            f"[bold red]Report generation failed:[/bold red] {error}"
        )
        raise typer.Exit(code=1) from error


@app.command()
def compare_schemas() -> None:
    """Compare the current schema with its registered baseline."""
    console.print(
        "[yellow]Schema comparison is not connected yet.[/yellow]"
    )


@app.command()
def schedule(
    cron: str = typer.Option(
        "0 9 * * *",
        "--cron",
        help="Five-field cron expression for scheduled validation.",
    ),
    config: str = typer.Option(
        "datasentinel/rules/sample.yaml",
        "--config",
        "-c",
        help="Path to the YAML validation configuration.",
    ),
) -> None:
    """Run scheduled dataset validation jobs."""

    def scheduled_validation() -> None:
        _run_validation(config)

    try:
        run_scheduler(
            job=scheduled_validation,
            cron_expression=cron,
        )
    except (ValueError, TypeError) as error:
        console.print(
            f"[bold red]Invalid schedule:[/bold red] {error}"
        )
        raise typer.Exit(code=1) from error


@app.command()
def list_rules() -> None:
    """List the supported YAML validation rules."""
    table = Table(title="Available Validation Rules")
    table.add_column("Rule Type")
    table.add_column("Purpose")

    table.add_row("null_check", "Check missing values")
    table.add_row("unique_check", "Check duplicate values")
    table.add_row("range", "Check numeric boundaries")
    table.add_row("regex", "Check text patterns")

    console.print(table)


if __name__ == "__main__":
    app()
