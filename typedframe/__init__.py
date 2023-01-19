
try:
    import pandas
except ImportError:
    pass
else:
    from typedframe.pandas_ import PandasTypedFrame as TypedDataFrame

try:
    import polars
except ImportError:
    pass
else:
    from typedframe.polars_ import PolarsTypedFrame

__version__ = '0.9.0'
