"""
Module for converting various input types to pandas DataFrames.

Provides functions to convert a variety of data structures into pandas
DataFrames, with options for handling missing data, resetting the index,
and custom behavior for specific input types.

Functions:
    to_df: Converts various input types to a pandas DataFrame, with options 
           for handling missing data and resetting the index.
    _ (list overload): Specialized behavior for converting a list of data to
                       a DataFrame.
    md_to_df: Convert Markdown to dataframe.
    html_to_df: Convert HTML to dataframe.
"""

from functools import singledispatch
from io import StringIO
from typing import Any, Dict

from pandas import DataFrame, Series, concat, read_csv
from pandas.core.generic import NDFrame

from .to_list import to_list


@singledispatch
def to_df(
    input_: Any,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: Dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame:
    """
    Converts various input types to a pandas DataFrame.

    Args:
        input_: The input data to convert into a DataFrame.
        drop_how: Specifies how missing values are dropped.
        drop_kwargs: Additional keyword arguments for DataFrame.dropna().
        reset_index: If True, the DataFrame index will be reset.
        **kwargs: Additional keyword arguments for DataFrame constructor.

    Returns:
        A pandas DataFrame constructed from the input data.

    Raises:
        ValueError: If there is an error during the conversion process.

    Note:
        This function is overloaded for different input types.
    """
    if drop_kwargs is None:
        drop_kwargs = {}

    try:
        df = DataFrame(input_, **kwargs)
        drop_kwargs["how"] = drop_how
        df = df.dropna(**drop_kwargs)
        return df.reset_index(drop=True) if reset_index else df
    except Exception as e:
        raise ValueError(f"Error converting input_ to DataFrame: {e}") from e


@to_df.register
def _(
    input_: list,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: Dict | None = None,
    reset_index: bool = True,
    **kwargs,
) -> DataFrame:
    """
    Specialized behavior for converting a list of data to a DataFrame.

    Args:
        input_: The input list to convert into a DataFrame.
        drop_how: Specifies how missing values are dropped.
        drop_kwargs: Additional keyword arguments for DataFrame.dropna().
        reset_index: If True, the DataFrame index will be reset.
        **kwargs: Additional keyword arguments for DataFrame constructor.

    Returns:
        A pandas DataFrame constructed from the input list.

    Raises:
        ValueError: If there is an error during the conversion process.
    """
    if not input_:
        return DataFrame()

    if not isinstance(input_[0], (DataFrame, Series, NDFrame)):
        if drop_kwargs is None:
            drop_kwargs = {}
        try:
            df = DataFrame(input_, **kwargs)
            df = df.dropna(**{**drop_kwargs, "how": drop_how})
            return df.reset_index(drop=True) if reset_index else df
        except Exception as e:
            raise ValueError(f"Error converting input_ to DataFrame: {e}") from e

    if drop_kwargs is None:
        drop_kwargs = {}
    try:
        df = concat(
            input_,
            axis=1 if all(isinstance(i, Series) for i in input_) else 0,
            **kwargs,
        )
    except Exception as e1:
        try:
            input_ = to_list(input_)
            df = input_[0]
            if len(input_) > 1:
                for i in input_[1:]:
                    df = concat([df, i], **kwargs)
        except Exception as e2:
            raise ValueError(
                f"Error converting input_ to DataFrame: {e1}, {e2}"
            ) from e2

    drop_kwargs["how"] = drop_how
    df.dropna(**drop_kwargs, inplace=True)
    return df.reset_index(drop=True) if reset_index else df


def md_to_df(md_str: str) -> DataFrame:
    """
    Convert Markdown to dataframe.

    Args:
        md_str: The markdown string to convert.

    Returns:
        A pandas DataFrame constructed from the markdown table.
    """
    md_str = md_str.replace('"', '""')
    md_str = md_str.replace("|", '","')
    lines = md_str.split("\n")
    md_str = "\n".join(lines[:1] + lines[2:])
    lines = md_str.split("\n")
    md_str = "\n".join([line[2:-2] for line in lines])

    if len(md_str) == 0:
        return None

    return read_csv(StringIO(md_str))


def html_to_df(html_str: str) -> DataFrame:
    """
    Convert HTML to dataframe.

    Args:
        html_str: The HTML string to convert.

    Returns:
        A pandas DataFrame constructed from the HTML table.

    Raises:
        ImportError: If the 'lxml' package is not installed.
    """
    try:
        from lxml import html
    except ImportError:
        raise ImportError(
            "You must install the `lxml` package to use this node parser."
        )

    tree = html.fromstring(html_str)
    table_element = tree.xpath("//table")[0]
    rows = table_element.xpath(".//tr")

    data = []
    for row in rows:
        cols = row.xpath(".//td")
        cols = [c.text.strip() if c.text is not None else "" for c in cols]
        data.append(cols)

    if len(data) == 0:
        return None

    if not all(len(row) == len(data[0]) for row in data):
        return None

    return DataFrame(data[1:], columns=data[0])