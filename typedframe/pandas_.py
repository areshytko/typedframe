
from typing import Type, TypeVar, Any
import pytz

import pandas as pd
import numpy as np

from typedframe.base import TypedDataFrameBase

try:
    from pandas.api.types import CategoricalDtype
except ImportError:
    from pandas.types.dtypes import CategoricalDtype

"""
dtype for datetime column
"""
DATE_TIME_DTYPE = np.dtype('datetime64[ns]')
UTC_DATE_TIME_DTYPE = pd.DatetimeTZDtype('ns', pytz.UTC)

T = TypeVar("T", bound="PandasTypedFrame")

_OBJECT_TYPES = {list, str, dict}


class PandasTypedFrame(TypedDataFrameBase):
    """
    Wrapper class over pandas
    """

    index_schema = (None, None)  # (name, dtype)

    @classmethod
    def convert(cls: Type[T], df: pd.DataFrame, add_optional_cols: bool = True) -> T:
        """
        Tries to convert a given dataframe and wrap in a typed dataframe.

        Examples
        --------

        >>> from typedframe.pandas_ import PandasTypedFrame, DATE_TIME_DTYPE
        >>> class MyTable(PandasTypedFrame):
        ...    schema = {
        ...       "col1": str,
        ...       "col2": np.int32,
        ...       "col3": ('foo', 'bar')
        ...    }
        ...    optional = {
        ...       "col4": bool,
        ...       "col5": DATE_TIME_DTYPE
        ...    }

        >>> df = pd.DataFrame({"col1": ['foo'], "col2": np.array([1], dtype=np.int32), "col3": ['bar']})
        >>> df.col3 = pd.Categorical(df.col3, categories=('foo', 'bar'), ordered=True)
        >>> print(MyTable.convert(df).df)
        """
        df = df.copy()

        if add_optional_cols:
            required = cls.dtype(with_optional=False)
            addon = {col: dtype for col, dtype in cls.dtype().items() if col not in df.columns and col not in required}
            df: pd.DataFrame = df if len(addon) == 0 else pd.concat(
                [df, pd.DataFrame(columns=addon.keys()).astype(addon)], axis=1)

        expected = cls.dtype()
        for col in df.columns:
            if col in expected:
                if isinstance(expected[col], tuple):
                    actual_cats = set(df[col].unique())
                    categories_diff = actual_cats.difference(set(expected[col]))
                    if categories_diff:
                        raise AssertionError(f"For column: {col} there are unknown categories: {categories_diff}")
                    df[col] = pd.Categorical(df[col], categories=expected[col], ordered=True)
                elif expected[col] == DATE_TIME_DTYPE:
                    df[col] = pd.to_datetime(df[col])
                elif expected[col] == UTC_DATE_TIME_DTYPE:
                    df[col] = pd.to_datetime(df[col], utc=True)
                else:
                    df[col] = df[col].astype(expected[col])

        if cls.index_schema[1]:
            df.index = df.index.astype(cls.index_schema[1])
            df.index.name = cls.index_schema[0]

        return cls(df)

    @classmethod
    def _extract_actual_dtypes(cls: Type[T], df: pd.DataFrame) -> dict:
        return df.dtypes.to_dict()

    @classmethod
    def _normalize_actual_dtype(cls: Type[T], dtype: Any) -> Any:
        if isinstance(dtype, CategoricalDtype):
            return tuple(dtype.categories)
        else:
            return dtype

    @classmethod
    def _normalize_expected_dtype(cls: Type[T], dtype: Any) -> Any:
        try:
            if dtype in _OBJECT_TYPES:
                return object
            else:
                return dtype
        except TypeError:
            return dtype

    def __init__(self, df: pd.DataFrame):

        if not isinstance(df, pd.DataFrame):
            raise AssertionError(f"Input argument of type {type(df)} is not an instance of pandas DataFrame")

        super().__init__(df)

        if self.index_schema[1]:
            if df.index.name != self.index_schema[0]:
                raise AssertionError(f"expected index name {self.index_schema[0]}, actual index name {df.index.name}")
            try:
                if self._dtypes_mismatch(df.index.dtype, self.index_schema[1]):
                    raise AssertionError(f"expected index dtype {self.index_schema[1]}, actual index dtype {df.index.dtype}")
            except TypeError:
                raise AssertionError(f"expected index dtype {self.index_schema[1]}, actual index dtype {df.index.dtype}")

        categoricals = [df[c] for c in df.columns if isinstance(df[c].dtype, CategoricalDtype)]
        for col in categoricals:
            if object != col.values.categories.dtype:
                raise AssertionError("Categoricals must have str categories")
            if np.nan in col.unique():
                raise AssertionError("Categoricals must not have NaNs")

        self.df = df
