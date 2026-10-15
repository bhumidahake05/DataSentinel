from typing import Literal

from pydantic import BaseModel, Field


class Rule(BaseModel):
    """Configuration for a single data-quality rule."""

    type: Literal[
        "null_check",
        "unique_check",
        "range",
        "regex",
    ]
    column: str
    parameters: dict[str, object] = Field(default_factory=dict)


class RuleConfig(BaseModel):
    """Complete YAML rule configuration."""

    name: str
    source: str
    rules: list[Rule]
