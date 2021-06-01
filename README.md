# typedframe
Typed Wrappers over Pandas DataFrames with schema validation.

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
