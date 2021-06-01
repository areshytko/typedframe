"""
Basic classes for typed wrappers over pandas dataframes
"""
from itertools import chain

import numpy as np
import pandas as pd

try:
    from pandas.api.types import CategoricalDtype
except ImportError:
    from pandas.types.dtypes import CategoricalDtype


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

    >>> class MyTable(TypedDataFrame):
    ...    schema = {
    ...        "col1": object, # str
    ...        "col2": np.int32,
    ...        "col3": 'category'
    ...    }
    ...    optional = {
    ...        "col4": bool,
               "col5": np.dtype('datetime64[ns]')
    ...    }

    >>> df = pd.DataFrame({"col1": ['foo'], "col2": np.array([1], dtype=np.int32), "col3": ['bar']})
    >>> df.col3 = df.col3.astype("category")
    >>> print(MyTable(df).df)
    """

    schema = {}

    optional = {}

    @classmethod
    def convert(cls, df: pd.DataFrame) -> 'TypedDataFrame':
        """
        Tries to convert a given dataframe and wrap in a typed dataframe.

        Examples
        --------

        >>> class MyTable(TypedDataFrame):
        ...    schema = {
        ...        "col1": object, # str
        ...        "col2": np.int32,
        ...        "col3": 'category'
        ...    }
        ...    optional = {
        ...        "col4": bool,
                   "col5": np.dtype('datetime64[ns]')
        ...    }

        >>> df = pd.DataFrame({"col1": ['foo'], "col2": [1], "col3": ['bar']})
        >>> print(MyTable.convert(df).df)
        """
        df = df.copy()
        expected = cls.dtype()
        for col in df.columns:
            if col in expected:
                if expected[col] == np.dtype('datetime64[ns]'):
                    df[col] = pd.to_datetime(df[col])
                else:
                    df[col] = df[col].astype(expected[col])

        return cls(df)

    @classmethod
    def dtype(cls, with_optional: bool = True) -> dict:
        """
        Combines schema of a current class and all super classes
        """
        return dict(chain(*(chain(cls.schema.items(), cls.optional.items())
                            if with_optional else cls.schema.items()
                            for cls in cls.__mro__[:-1])))

    def __init__(self, df: pd.DataFrame):

        actual_dtypes = {item[0]: _normalize_dtype(item[1])
                         for item in df.dtypes.to_dict().items()}
        expected = self.dtype(with_optional=False).items()

        diff = set()
        for col, dtype in expected:
            try:
                if col not in actual_dtypes or dtype != actual_dtypes[col]:
                    diff.add((col, dtype))
            except TypeError:
                diff.add((col, dtype))

        optional = self.dtype().items()
        for col, dtype in optional:
            try:
                if col in actual_dtypes and dtype != actual_dtypes[col]:
                    diff.add((col, dtype))
            except TypeError:
                diff.add((col, dtype))

        if diff:
            raise AssertionError(
                "Dataframe doesn't match schema\n"
                f"Actual: {actual_dtypes}\nExpected: {self.dtype()}\nDirrerence: {diff}"
            )

        categoricals = (df[c] for c in df.columns if isinstance(df[c].dtype, CategoricalDtype))
        msg = "Categoricals must have str categories"
        assert all(object == c.values.categories.dtype for c in categoricals), msg

        addon = {col: dtype for col, dtype in self.dtype().items() if col not in df.columns}
        self.df = df if len(addon) == 0 else pd.concat(
            [df, pd.DataFrame(columns=addon.keys()).astype(addon)], axis=1)


def _normalize_dtype(dtype):
    if isinstance(dtype, CategoricalDtype):
        return 'category'
    else:
        return dtype
