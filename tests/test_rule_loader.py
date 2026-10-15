from pathlib import Path

from datasentinel.rules.loader import load_rule_config


def test_load_rule_config() -> None:
    """Test loading a valid YAML rule configuration."""
    path = Path("rules/sample.yaml")

    config = load_rule_config(str(path))

    assert config.name == "sample_data_quality"
    assert config.source == "data/sample.csv"
    assert len(config.rules) == 4


def test_rule_types() -> None:
    """Test that all required rule types are loaded."""
    config = load_rule_config("rules/sample.yaml")

    rule_types = [rule.type for rule in config.rules]

    assert rule_types == [
        "null_check",
        "unique_check",
        "range",
        "regex",
    ]