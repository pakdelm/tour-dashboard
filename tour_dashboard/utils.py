import os
from typing import Any

from pandas import DataFrame


def create_os_independent_path(path: str) -> str:
    # First normalize the path string into a proper string for the OS.
    # Then os.sep must be safe to use as a delimiter in string function split.
    split_path = os.path.normpath(path).split(os.path.sep)
    # splat to iterate through list
    joined_path = os.path.join(*split_path)

    return joined_path

def value_exists_in_dataframe(df: DataFrame, value:Any) -> bool:

    result = value in df.values
    return result

def entry_exists_in_table_data(df_to_write:DataFrame, df_table:DataFrame) -> bool:
    df_to_write_ids = df_to_write.hash_id.unique()
    df_table_ids = df_table.hash_id.unique()
    return any(item in df_to_write_ids for item in df_table_ids)

def file_exists(path:str) -> bool:
    return os.path.isfile(path)