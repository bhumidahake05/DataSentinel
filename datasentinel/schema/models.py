from dataclasses import dataclass


@dataclass
class SchemaChange:
    """Represent a change between two dataset schemas."""

    change_type: str
    column: str
    old_type: str | None
    new_type: str | None
    