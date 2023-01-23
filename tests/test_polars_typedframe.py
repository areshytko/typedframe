import datetime

import polars as pl
import pytest

from typedframe.polars_ import PolarsTypedFrame as TypedDataFrame


class ParentDataFrame(TypedDataFrame):
    schema = {
        'int_field': pl.Int16,
        'float_field': pl.Float64,
        'bool_field': pl.Boolean,
        'str_field': pl.Utf8,
        'date_field': pl.Date,
        'datetime_field': pl.Datetime
    }


class MixinDataFrame(TypedDataFrame):
    schema = {
        'mixin_field': pl.Int64
    }


class ChildDataFrame(ParentDataFrame, MixinDataFrame):
    schema = {
        'new_field': pl.Int64
    }


class OptionalDataFrame(TypedDataFrame):
    schema = {
        'required': pl.Boolean
    }
    optional = {
        'optional': pl.Boolean
    }


def test_base_success_case():
    df = pl.DataFrame({'int_field': [1, 2, 3],
                       'float_field': [1.0, 2.0, 3.0],
                       'bool_field': [True, False, True],
                       'str_field': ['a', 'b', 'c'],
                       'date_field': [datetime.date(2021, 5, 31), datetime.date(2021, 6, 1), datetime.date(2021, 6, 2)],
                       'datetime_field': [datetime.datetime(2021, 5, 31, 12, 0, 0), datetime.datetime(2021, 6, 1, 12, 0, 0), datetime.datetime(2021, 6, 2, 12, 0, 0)],
                       'mixin_field': [1, 2, 3],
                       'new_field': [1, 2, 3]})
    df = df.with_column(pl.col('int_field').cast(pl.Int16))
    _ = ChildDataFrame(df)


def test_base_error_case():
    df = pl.DataFrame({'int_field': [1, 2, 3],
                       'float_field': [1.0, 2.0, 3.0],
                       'bool_field': [True, False, True],
                       'str_field': ['a', 'b', 'c'],
                       'new_field': [1, 2, 3]})
    with pytest.raises(AssertionError):
        _ = ChildDataFrame(df)


def test_convert_success_case():
    df = pl.DataFrame({'int_field': [1, 2, 3],
                       'float_field': [1.0, 2.0, 3.0],
                       'bool_field': [True, False, True],
                       'str_field': ['a', 'b', 'c'],
                       'date_field': [datetime.date(2021, 5, 31), datetime.date(2021, 6, 1), datetime.date(2021, 6, 2)],
                       'datetime_field': [datetime.datetime(2021, 5, 31, 12, 0, 0),
                                          datetime.datetime(2021, 6, 1, 12, 0, 0),
                                          datetime.datetime(2021, 6, 2, 12, 0, 0)]})
    _ = ParentDataFrame.convert(df)


def test_convert_error_case():
    df = pl.DataFrame({'int_field': [1, 2, 3],
                       'float_field': [1.0, 2.0, 3.0],
                       'bool_field': [True, False, True],
                       'str_field': ['a', 'b', 'c']})
    with pytest.raises(AssertionError):
        _ = ParentDataFrame.convert(df)


def test_optional_success_case():
    df = pl.DataFrame({'required': [True, False, True]})
    _ = OptionalDataFrame(df)


def test_optional_success_case_2():
    df = pl.DataFrame({'required': [True, False, True],
                       'optional': [True, False, True]})
    _ = OptionalDataFrame(df)


def test_optional_error_case():
    df = pl.DataFrame({'required': [True, False, True],
                       'optional': [2, 3, 1]})
    with pytest.raises(AssertionError):
        _ = OptionalDataFrame(df)


def test_convert_optional():
    df = pl.DataFrame({'required': [True]})
    data = OptionalDataFrame.convert(df, add_optional_cols=True)
    assert all(col in data.df.columns for col in OptionalDataFrame.dtype().keys())
