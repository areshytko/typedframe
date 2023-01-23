
import abc
import datetime

import pandas as pd
import numpy as np
import pytest

from typedframe.pandas_ import UTC_DATE_TIME_DTYPE, DATE_TIME_DTYPE, PandasTypedFrame as TypedDataFrame


class MyDataFrame(TypedDataFrame):
    schema = {
        'int_field': np.int16,
        'float_field': np.float64,
        'bool_field': bool,
        'str_field': str,
        'obj_field': object
    }


class InheritedDataFrame(MyDataFrame):
    schema = {
        'new_field': np.int64
    }


class DataFrameWithOptional(TypedDataFrame):
    schema = {
        'required': bool
    }
    optional = {
        'optional': bool
    }


class IndexDataFrame(TypedDataFrame):
    schema = {
        'foo': bool
    }

    index_schema = ('bar', DATE_TIME_DTYPE)


class ChildIndexDataFrame(IndexDataFrame):
    pass


class UTCDateTimeDataframe(TypedDataFrame):
    schema = {
        'date_field': UTC_DATE_TIME_DTYPE
    }


def test_utc_datetime_success_case():
    df = pd.DataFrame({'date_field': [datetime.date.today(), datetime.date(2021, 5, 31)]})
    df.date_field = pd.to_datetime(df.date_field, utc=True)
    _ = UTCDateTimeDataframe(df)


def test_utc_datetime_error_case():
    df = pd.DataFrame({'date_field': [datetime.date.today(), datetime.date(2021, 5, 31)]})
    df.date_field = pd.to_datetime(df.date_field)
    with pytest.raises(AssertionError):
        _ = UTCDateTimeDataframe(df)


def test_utc_datetime_convert_case():
    df = pd.DataFrame({'date_field': [datetime.date.today(), datetime.date(2021, 5, 31)]})
    _ = UTCDateTimeDataframe.convert(df)


def test_index_success_case():
    df = pd.DataFrame({'foo': [True, False]})
    df.index = pd.to_datetime(pd.Series([datetime.date.today(), datetime.date(2021, 5, 31)], name='bar'))
    _ = IndexDataFrame(df)
    _ = ChildIndexDataFrame(df)


def test_index_fail_case():
    df = pd.DataFrame({'foo': [True, False]})
    with pytest.raises(AssertionError):
        _ = IndexDataFrame(df)


def test_index_convert_success_case():
    df = pd.DataFrame({'foo': [True, False]})
    df.index = pd.Series(['2021-06-03', '2021-05-31'])
    _ = IndexDataFrame.convert(df)


def test_base_success_case():
    df = pd.DataFrame({
        'int_field': np.int16([1, 2]),
        'float_field': np.float64([0.1, 0.2]),
        'bool_field': [True, False],
        'str_field': ["one", "two"],
        'obj_field': ["", ""],
        'new_field': np.int64([10, 20])
    })
    _ = InheritedDataFrame(df)


class CategoricalFrame(TypedDataFrame):
    schema = {
        'col': ('foo', 'bar')
    }


def test_categorical_success_1():
    df = pd.DataFrame({'col': ['foo', 'foo', 'bar']})
    df.col = pd.Categorical(df.col, categories=('foo', 'bar'), ordered=True)
    _ = CategoricalFrame(df)


def test_categorical_success_2():
    df = pd.DataFrame({'col': ['foo', 'foo']})
    df.col = pd.Categorical(df.col, categories=('foo', 'bar'), ordered=True)
    _ = CategoricalFrame(df)


def test_categorical_failure_1():
    df = pd.DataFrame({'col': ['foo', 'foo']})
    df.col = pd.Categorical(df.col, categories=('foo', 'bar', 'buzz'), ordered=True)
    with pytest.raises(AssertionError):
        _ = CategoricalFrame(df)


def test_categorical_failure_3():
    df = pd.DataFrame({'col': ['foo', 'foo']})
    with pytest.raises(AssertionError):
        _ = CategoricalFrame(df)


def test_convert_categorical():
    df = pd.DataFrame({'col': ['foo', 'foo']})
    _ = CategoricalFrame.convert(df)


def test_convert_optional():
    df = pd.DataFrame({'required': [True]})
    data = DataFrameWithOptional.convert(df, add_optional_cols=True)
    assert all(col in data.df.columns for col in DataFrameWithOptional.dtype().keys())


def test_convert_categorical_failure():
    df = pd.DataFrame({'col': ['foo', 'buzz']})
    with pytest.raises(AssertionError):
        _ = CategoricalFrame.convert(df)


def test_categorical_with_nans_failure():
    df = pd.DataFrame({'col': ['foo', 'buzz']})
    df.col = pd.Categorical(df.col, categories=CategoricalFrame.schema['col'], ordered=True)
    with pytest.raises(AssertionError):
        _ = CategoricalFrame(df)


class PingInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def ping(self):
        pass


class Parent(TypedDataFrame):
    schema = {
        'foo': bool
    }


class Child(Parent, PingInterface):
    
    schema = {
        'bar': bool
    }

    def ping(self):
        print("ping")


def test_multiple_inheritance_1_success():
    _ = Child(pd.DataFrame({'foo': [True], 'bar': [False]}))


def test_multiple_inheritance_1_failure():
    with pytest.raises(AssertionError):
        _ = Child(pd.DataFrame({'bar': [False]}))


class Root(TypedDataFrame):
    
    schema = {
        'root': bool
    }


class Left(Root):
    schema = {
        'left': bool
    }


class Right(Root):
    schema = {
        'root': object,
        'right': bool
    }


class Down(Left, Right):
    pass


def test_multiple_inheritance_2_success():
    _ = Down(pd.DataFrame({'root': [True], 'left': [True], 'right': [True]}))


def test_multiple_inheritance_2_failure():
    with pytest.raises(AssertionError):
        _ = Down(pd.DataFrame({'root': [True], 'left': [True]}))


def test_multiple_inheritance_2_failure_with_root_overwrite():
    with pytest.raises(AssertionError):
        _ = Down(pd.DataFrame({'root': [True], 'left': [True], 'right': ['string']}))
