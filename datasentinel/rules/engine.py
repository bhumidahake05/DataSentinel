from dataclasses import dataclass

import pandas as pd

from datasentinel.connectors.dataset import DataSet
from datasentinel.rules.models import Rule


@dataclass
class RuleResult:
    """Result produced by a single quality rule."""

    rule_type: str
    column: str
    passed: bool
    violations: int
    message: str


class RuleEngine:
    """Execute configured data-quality rules."""

    def run_rule(
        self,
        dataset: DataSet,
        rule: Rule,
    ) -> RuleResult:
        """Execute one configured rule."""
        if rule.type == "null_check":
            return self._null_check(dataset.data, rule)

        if rule.type == "unique_check":
            return self._unique_check(dataset.data, rule)

        if rule.type == "range":
            return self._range_check(dataset.data, rule)

        if rule.type == "regex":
            return self._regex_check(dataset.data, rule)

        raise ValueError(f"Unsupported rule type: {rule.type}")

    @staticmethod
    def _check_column(
        data: pd.DataFrame,
        column: str,
    ) -> None:
        """Verify that the requested column exists."""
        if column not in data.columns:
            raise ValueError(
                f"Column '{column}' does not exist in the dataset."
            )

    def _null_check(
        self,
        data: pd.DataFrame,
        rule: Rule,
    ) -> RuleResult:
        """Check the number of null values in a column."""
        self._check_column(data, rule.column)

        allowed_nulls_value = rule.parameters.get("allowed_nulls", 0)
        allowed_nulls = int(str(allowed_nulls_value))


        null_count = int(data[rule.column].isna().sum())
        passed = null_count <= allowed_nulls

        return RuleResult(
            rule_type=rule.type,
            column=rule.column,
            passed=passed,
            violations=max(0, null_count - allowed_nulls),
            message=(
                f"Found {null_count} null values; "
                f"allowed {allowed_nulls}."
            ),
        )

    def _unique_check(
        self,
        data: pd.DataFrame,
        rule: Rule,
    ) -> RuleResult:
        """Check that values in a column are unique."""
        self._check_column(data, rule.column)

        duplicate_count = int(
            data[rule.column].duplicated().sum()
        )

        return RuleResult(
            rule_type=rule.type,
            column=rule.column,
            passed=duplicate_count == 0,
            violations=duplicate_count,
            message=(
                f"Found {duplicate_count} duplicate values."
            ),
        )

    def _range_check(
        self,
        data: pd.DataFrame,
        rule: Rule,
    ) -> RuleResult:
        """Check whether numeric values are within a configured range."""
        self._check_column(data, rule.column)

        minimum_value = rule.parameters["min"]
        maximum_value = rule.parameters["max"]

        minimum = float(str(minimum_value))
        maximum = float(str(maximum_value))

        invalid = (
            (data[rule.column] < minimum)
            | (data[rule.column] > maximum)
        )

        violation_count = int(invalid.sum())

        return RuleResult(
            rule_type=rule.type,
            column=rule.column,
            passed=violation_count == 0,
            violations=violation_count,
            message=(
                f"Expected values between {minimum} and "
                f"{maximum}; found {violation_count} violations."
            ),
        )

    def _regex_check(
        self,
        data: pd.DataFrame,
        rule: Rule,
    ) -> RuleResult:
        """Check values against a configured regular expression."""
        self._check_column(data, rule.column)

        pattern = str(rule.parameters["pattern"])

        values = data[rule.column].fillna("").astype(str)

        matches = values.str.fullmatch(pattern, na=False)
        violation_count = int((~matches).sum())

        return RuleResult(
            rule_type=rule.type,
            column=rule.column,
            passed=violation_count == 0,
            violations=violation_count,
            message=(
                f"Found {violation_count} values that do not "
                f"match the configured pattern."
            ),
        )