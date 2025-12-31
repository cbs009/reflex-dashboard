import pandas as pd
from typing import Dict, Optional

class DataStore:
    """
    Global in-memory store for large datasets to avoid Reflex State serialization issues.
    Data is keyed by session token to ensure multi-user isolation.
    """
    _sales_data: Dict[str, pd.DataFrame] = {}
    _courier_data: Dict[str, pd.DataFrame] = {}

    @classmethod
    def set_sales_data(cls, token: str, df: pd.DataFrame):
        cls._sales_data[token] = df

    @classmethod
    def get_sales_data(cls, token: str) -> Optional[pd.DataFrame]:
        return cls._sales_data.get(token)

    @classmethod
    def set_courier_data(cls, token: str, df: pd.DataFrame):
        cls._courier_data[token] = df

    @classmethod
    def get_courier_data(cls, token: str) -> Optional[pd.DataFrame]:
        return cls._courier_data.get(token)

    @classmethod
    def clear_session(cls, token: str):
        if token in cls._sales_data:
            del cls._sales_data[token]
        if token in cls._courier_data:
            del cls._courier_data[token]
