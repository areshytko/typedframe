from typing import Any
from typing import Type, TypeVar, Any

import polars as pl

from typedframe.base import TypedDataFrameBase

T = TypeVar("T", bound="PolarsTypedFrame")


class PolarsTypedFrame(TypedDataFrameBase):

    @classmethod
    def convert(cls: Type["T"], df: pl.DataFrame, add_optional_cols: bool = True) -> T:

        addon = {}
        if add_optional_cols:
            required = cls.dtype(with_optional=False)
            addon = {col: dtype for col, dtype in cls.dtype().items() if col not in df.columns and col not in required}

        expected = cls.dtype()
        df = df.with_columns([
            pl.col(col).cast(expected[col]) for col in df.columns if col in expected
        ] + [
            pl.lit(None, dtype=dtype).alias(col) for col, dtype in addon.items()
        ])
        return cls(df)

    @classmethod
    def _extract_actual_dtypes(cls, df: pl.DataFrame) -> dict:
        return dict(zip(df.columns, df.dtypes))

    @classmethod
    def _normalize_actual_dtype(cls, dtype: Any) -> Any:
        return dtype

    @classmethod
    def _normalize_expected_dtype(cls, dtype: Any) -> Any:
        return dtype

    def __init__(self, df: pl.DataFrame):

        if not isinstance(df, pl.DataFrame):
            raise AssertionError(f"Input argument of type {type(df)} is not an instance of polars DataFrame")

        super().__init__(df)
        self.df = df
