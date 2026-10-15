from dataclasses import dataclass

import pandas as pd


@dataclass
class DataSet:
    """Unified representation of data loaded by a connector."""

    data: pd.DataFrame
    source: str