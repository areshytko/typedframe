
import pandas as pd
import numpy as np
import datetime

import pytest

from typedframe import TypedDataFrame, DATE_TIME_DTYPE, STRING_DTYPE


class MyDataFrame(TypedDataFrame):
    schema = {
        'int_field': np.int16,
        'float_field': np.float64,
        'bool_field': bool,
        'str_field': STRING_DTYPE,
        'date_field': DATE_TIME_DTYPE
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
        
    })


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