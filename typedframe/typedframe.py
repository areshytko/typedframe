"""
Basic classes for typed wrappers over pandas dataframes
"""
from itertools import chain
from typing import Type, TypeVar
import pytz

import numpy as np
import pandas as pd

try:
    from pandas.api.types import CategoricalDtype
except ImportError:
    from pandas.types.dtypes import CategoricalDtype

"""
dtype for datetime column
"""
DATE_TIME_DTYPE = np.dtype('datetime64[ns]')
UTC_DATE_TIME_DTYPE = pd.DatetimeTZDtype('ns', pytz.UTC)

T = TypeVar("T", bound="TypedDataFrame")

class TypedDataFrame:
    """
    Wrapper class over pandas.DataFrame to provide explicit schema specs.

    Provide expected dataframe schema in schema static variable.
    Provide optional columns in optional static variable.
    All columns from optional schema that are missing in a wrapped dataframe will be added with NaN values.

    Schemas can be inheritted via Python class inheritance. The semantics of it is the following:
    all columns of the parent are also included to a child schema.

    Examples
    --------

    >>> from typedframe import TypedDataFrame, DATE_TIME_DTYPE
    >>> class MyTable(TypedDataFrame):
    ...    schema = {
    ...        "col1": str,
    ...        "col2": np.int32,
    ...        "col3": ('foo', 'bar')
    ...    }
    ...    optional = {
    ...        "col4": bool,
               "col5": DATE_TIME_DTYPE
    ...    }

    >>> df = pd.DataFrame({"col1": ['foo'], "col2": np.array([1], dtype=np.int32), "col3": ['bar']})
    >>> df.col3 = pd.Categorical(df.col3, categories=('foo', 'bar'), ordered=True)
    >>> print(MyTable(df).df)
    """

    schema = {}

    index_schema = (None, None)  # (name, dtype)

    optional = {}

    @classmethod
    def convert(cls: Type[T], df: pd.DataFrame) -> T:
        """
        Tries to convert a given dataframe and wrap in a typed dataframe.

        Examples
        --------

        >>> from typedframe import TypedDataFrame, DATE_TIME_DTYPE
        >>> class MyTable(TypedDataFrame):
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
    def dtype(cls, with_optional: bool = True) -> dict:
        """
        Combines schema of a current class and all super classes
        """
        return dict(chain(*(chain(cls.schema.items(), cls.optional.items())
                            if with_optional else cls.schema.items()
                            for cls in cls.__mro__[:-1] if hasattr(cls, 'schema'))))

    def __init__(self, df: pd.DataFrame):

        if not isinstance(df, pd.DataFrame):
            raise AssertionError(f"Input argument of type {type(df)} is not an instance of pandas DataFrame")

        actual_dtypes = df.dtypes.to_dict()
        expected = self.dtype(with_optional=False).items()

        diff = set()
        for col, dtype in expected:
            try:
                if col not in actual_dtypes or _dtypes_dismatch(actual_dtypes[col], dtype):
                    diff.add((col, dtype))
            except TypeError:
                diff.add((col, dtype))

        optional = self.dtype().items()
        for col, dtype in optional:
            try:
                if col in actual_dtypes and _dtypes_dismatch(actual_dtypes[col], dtype):
                    diff.add((col, dtype))
            except TypeError:
                diff.add((col, dtype))
        
        if self.index_schema[1]:
            if df.index.name != self.index_schema[0]:
                diff.add(f"expected index name {self.index_schema[0]}, actual index name {df.index.name}")
            try:
                if _dtypes_dismatch(df.index.dtype, self.index_schema[1]):
                    diff.add(f"expected index dtype {self.index_schema[1]}, actual index dtype {df.index.dtype}")
            except TypeError:
                diff.add(f"expected index dtype {self.index_schema[1]}, actual index dtype {df.index.dtype}")

        if diff:
            actual = {key: _normalize_actual_dtype(value) for key, value in df.dtypes.to_dict().items()}
            expected = {key: _normalize_expected_dtype(value) for key, value in self.dtype().items()}
            raise AssertionError(
                "Dataframe doesn't match schema\n"
                f"Actual: {actual}\nExpected: {expected}\nDifference: {diff}"
            )

        categoricals = [df[c] for c in df.columns if isinstance(df[c].dtype, CategoricalDtype)]
        for col in categoricals:
            if object != col.values.categories.dtype:
                raise AssertionError("Categoricals must have str categories")
            if np.nan in col.unique():
                raise AssertionError("Categoricals must not have NaNs")

        addon = {col: dtype for col, dtype in self.dtype().items() if col not in df.columns}
        self.df: pd.DataFrame = df if len(addon) == 0 else pd.concat(
            [df, pd.DataFrame(columns=addon.keys()).astype(addon)], axis=1)


def _normalize_actual_dtype(dtype):
    if isinstance(dtype, CategoricalDtype):
        return tuple(dtype.categories)
    else:
        return dtype


_OBJECT_TYPES = {list, str, dict}


def _normalize_expected_dtype(dtype):
    try:
        if dtype in _OBJECT_TYPES:
            return object
        else:
            return dtype
    except TypeError:
        return dtype 


def _dtypes_dismatch(actual, expected) -> bool:
    actual = _normalize_actual_dtype(actual)
    expected = _normalize_expected_dtype(expected)
    return actual != expected
