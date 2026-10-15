from pathlib import Path

import yaml

from datasentinel.rules.models import RuleConfig


def load_rule_config(path: str) -> RuleConfig:
    """Load and validate a YAML rule configuration."""
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Rule configuration not found: {path}"
        )

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return RuleConfig.model_validate(data)
