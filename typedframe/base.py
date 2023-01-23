"""
Basic classes for typed wrappers over dataframes
"""
from abc import abstractmethod
from itertools import chain
from typing import Type, TypeVar, Any


T = TypeVar("T", bound="TypedDataFrameBase")


class TypedDataFrameBase:
    """
    Wrapper class over DataFrame to provide explicit schema specs.

    Provide expected dataframe schema in schema static variable.
    Provide optional columns in optional static variable.
    All columns from optional schema that are missing in a wrapped dataframe will be added with NaN values.

    Schemas can be inheritted via Python class inheritance. The semantics of it is the following:
    all columns of the parent are also included to a child schema.
    """

    schema = {}

    optional = {}

    @classmethod
    @abstractmethod
    def convert(cls: Type[T], df, add_optional_cols: bool = True) -> T:
        pass

    @classmethod
    def dtype(cls: Type[T], with_optional: bool = True) -> dict:
        """
        Combines schema of a current class and all super classes
        """
        return dict(chain(*(chain(cls.schema.items(), cls.optional.items())
                            if with_optional else cls.schema.items()
                            for cls in cls.__mro__[:-1] if hasattr(cls, 'schema'))))

    @classmethod
    def _extract_actual_dtypes(cls: Type[T], df) -> dict:
        return cls._extract_actual_dtypes(df)

    @classmethod
    @abstractmethod
    def _normalize_actual_dtype(cls: Type[T], dtype: Any) -> Any:
        pass

    @classmethod
    @abstractmethod
    def _normalize_expected_dtype(cls: Type[T], dtype: Any) -> Any:
        pass

    @classmethod
    def _dtypes_mismatch(cls: Type[T], actual: Any, expected: Any) -> bool:
        actual = cls._normalize_actual_dtype(actual)
        expected = cls._normalize_expected_dtype(expected)
        return actual != expected

    def __init__(self, df):

        actual_dtypes = self._extract_actual_dtypes(df)
        expected = self.dtype(with_optional=False).items()

        diff = set()
        for col, dtype in expected:
            try:
                if col not in actual_dtypes or self._dtypes_mismatch(actual_dtypes[col], dtype):
                    diff.add((col, dtype))
            except TypeError:
                diff.add((col, dtype))

        optional = self.dtype().items()
        for col, dtype in optional:
            try:
                if col in actual_dtypes and self._dtypes_mismatch(actual_dtypes[col], dtype):
                    diff.add((col, dtype))
            except TypeError:
                diff.add((col, dtype))

        if diff:
            actual = {key: self._normalize_actual_dtype(value) for key, value in actual_dtypes.items()}
            expected = {key: self._normalize_expected_dtype(value) for key, value in self.dtype().items()}
            raise AssertionError(
                "Dataframe doesn't match schema\n"
                f"Actual: {actual}\nExpected: {expected}\nDifference: {diff}"
            )
