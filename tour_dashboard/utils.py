"""
utils for path generation and assertions
"""
import logging
import os
import json
from typing import Any, Dict, List, Optional

from pandas import DataFrame


# pylint: disable=C0103

def create_os_independent_path(path: str) -> str:
    """
    Return os independent path
	:param path: path to render os-independent
	:return: os-independent path
	"""
    # First normalize the path string into a proper string for the OS.
    # Then os.sep must be safe to use as a delimiter in string function split.
    split_path = os.path.normpath(path).split(os.path.sep)
    # splat to iterate through list
    joined_path = os.path.join(*split_path)

    return joined_path


def value_exists_in_dataframe(df: DataFrame, value: Any) -> bool:
    """
    Assert if value exists in DataFrame in all columns
    :param df: pandas DataFrame
    :param value: Value to assert
    :return: True, if value exists in DataFrame
    """

    result = value in df.values
    return result


def entry_exists_in_table_data(df_to_write: DataFrame, df_table: DataFrame) -> bool:
    """
    Assert whether entry exists in DataFrame by comparing hash_ids from DataFrame that should be
    written to database and the loaded database DataFrame itself
    :param df_to_write: DataFrame with one parsed and analyzed gpx/tour data. Should contain one
    tour name from gpx schema
    :param df_table: Loaded DataFrame from database
    :return: True, if entry already exists in database DataFrame
    """
    tour_name = df_to_write.tour_name.unique()

    df_to_write_ids = df_to_write.hash_id.unique()
    df_table_ids = df_table.hash_id.unique()

    result = any(item in df_to_write_ids for item in df_table_ids)

    if result:
        logging.info("Tour: %s already exists in database.", tour_name)
    else:
        logging.info("Tour: %s is a new entry.", tour_name)

    return result


def file_exists(path: str) -> bool:
    """
    Assert whether file exists from input path
    :param path: Path to assert
    :return: True, if file exists
    """
    return os.path.isfile(path)


def create_file_paths_with_extension(directory: str, extension: str) -> List[str]:
    """
    Create a list of file paths for input extension in given directory
    :param directory: path to directory with files
    :param extension: file extension that should be considered
    :return: List of files within input directory that contain input extension
    """
    file_paths = []

    for file in os.listdir(directory):
        if file.endswith(extension):
            file_with_extension = os.path.join(directory, file)
            file_path = create_os_independent_path(file_with_extension)
            file_paths.append(file_path)

    return file_paths


def parse_json(path: str) -> Optional[Dict[str, str]]:
    """
	Parse json to dict, if path exists
	:param path: path to json file to be parsed
	:return: dict from json
	"""
    try:
        with open(file=path, mode='r', encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as error:
        print("File not found")
        print(error)
        raise
