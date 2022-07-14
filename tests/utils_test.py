import pytest
from sqlalchemy import create_engine
import pandas as pd
from tour_dashboard import utils, data_processing


def test_create_os_independent_path():
    input = "../data/data.db"
    expected = "..\\data\\data.db"
    assert utils.create_os_independent_path(input) == expected

def test_entry_exists_in_table_data():
    path = "../tests/test_resources/gpx_distances.gpx"
    database_path = 'sqlite:///../data/data.db'
    table_name = 'tour_data'

    df_to_write = data_processing.prepare_gpx_data_for_database(path)
    engine = create_engine(database_path, echo=False)

    query = f"SELECT * FROM {table_name}"
    df_table = pd.read_sql_query(query, engine)

    result = utils.entry_exists_in_table_data(df_to_write, df_table)
    assert result == True

def test_create_file_paths_with_extension():
    dir = "../tests/test_resources"
    extension = ".gpx"
    source_file_paths = utils.create_file_paths_with_extension(dir, extension)

    test_files = ["tests/test_resources/gpx_distances.gpx", "tests/test_resources/gpx_read_data.gpx"]
    path_prefix = "../"
    expected_file_paths = [utils.create_os_independent_path(path_prefix+element) for element in test_files]

    assert source_file_paths == expected_file_paths

def test_parse_json():
    path_to_json = "../tests/test_resources/db_credentials_test.json"
    path_to_nothing = "../tests/test_resources/no_file.json"

    parsed_dict = utils.parse_json(path_to_json)

    expected_dict = {
        "userName": "your_user_name",
        "password": "your_password",
        "host": "127.0.0.1",
        "port": "3306",
        "databaseName": "your_database_name",
        "tableName" : "your_table_name"
    }

    assert parsed_dict == expected_dict

    with pytest.raises(FileNotFoundError):
        utils.parse_json(path_to_nothing)