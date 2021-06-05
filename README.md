# 🐍 typedframe

**Typed wrappers over pandas DataFrames with schema validation.**

`TypedDataFrame` is a lightweight wrapper over `pandas.DataFrame` that provides runtime schema validation and can be used to establish strong data contracts between interfaces in your Python code.

```python
    >>> from typedframe import TypedDataFrame
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
```


## Supported Data Types

- Integers: `np.int16`, `np.int32`, `np.int64`, etc.
- Floats: `np.float16`, `np.float32`, `np.float64`, etc.
- Boolean: `bool`
- String: `STRING_DTYPE`
- Python object: `object`
- Categorical: `category`
- Date, Datetime: `DATE_TIME_DTYPE`

