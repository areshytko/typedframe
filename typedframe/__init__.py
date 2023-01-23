
try:
    import pandas
except ImportError:
    pass
else:
    from typedframe.pandas_ import PandasTypedFrame as TypedDataFrame, DATE_TIME_DTYPE, UTC_DATE_TIME_DTYPE

try:
    import polars
except ImportError:
    pass
else:
    from typedframe.polars_ import PolarsTypedFrame

__version__ = '0.10.0'
