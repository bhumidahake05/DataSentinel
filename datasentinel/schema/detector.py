import pandas as pd

from datasentinel.schema.models import SchemaChange


class SchemaDriftDetector:
    """Detect changes between a baseline and current schema."""

    @staticmethod
    def get_schema(data: pd.DataFrame) -> dict[str, str]:
        """Return column names and their data types."""
        return {
            str(column): str(dtype)
            for column, dtype in data.dtypes.items()
        }

    def compare(
        self,
        baseline: dict[str, str],
        current: dict[str, str],
    ) -> list[SchemaChange]:
        """Compare baseline and current schemas."""
        changes: list[SchemaChange] = []

        baseline_columns = set(baseline)
        current_columns = set(current)

        for column in sorted(current_columns - baseline_columns):
            changes.append(
                SchemaChange(
                    change_type="added",
                    column=column,
                    old_type=None,
                    new_type=current[column],
                )
            )

        for column in sorted(baseline_columns - current_columns):
            changes.append(
                SchemaChange(
                    change_type="removed",
                    column=column,
                    old_type=baseline[column],
                    new_type=None,
                )
            )

        common_columns = baseline_columns & current_columns

        for column in sorted(common_columns):
            if baseline[column] != current[column]:
                changes.append(
                    SchemaChange(
                        change_type="type_changed",
                        column=column,
                        old_type=baseline[column],
                        new_type=current[column],
                    )
                )

        return changes