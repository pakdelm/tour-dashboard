import pandas as pd
import pytest
import sqlalchemy
from pandas._testing import assert_frame_equal

from tour_dashboard import data_processing, database

gpx_path = "../tests/test_resources/gpx_distances.gpx"
database_path = '../tests/test_resources/test_data.db'

def test_create_mysql_url():
    test_credentials = {
        "user": "your_user_name",
        "password": "your_password",
        "host": "127.0.0.1",
        "port": "3306",
        "database": "your_database_name"
    }
    actual_url = database.create_mysql_url(test_credentials)
    expected_url = "mysql+pymysql://your_user_name:your_password@127.0.0.1:3306/your_database_name"
    assert actual_url == expected_url


def test_create_sqlite_url():
    _path = "path/to/database"
    actual_url = database.create_sqlite_url(_path)
    expected_url = "sqlite:///" + _path
    assert actual_url == expected_url


def test_table_exists():
    table_name = "test_table_exists"
    url = database.create_sqlite_url(database_path)
    engine = sqlalchemy.create_engine(url, echo=False)

    assert database.table_exists(engine, table_name) == False

    df = pd.DataFrame.from_dict({'col_1': [3], 'col_2': ['a']})
    df.to_sql(table_name, con=engine, if_exists='append')

    assert database.table_exists(engine, table_name) == True

def test_load_df_from_database():
    table_name = "test_load_df_from_database"
    url = database.create_sqlite_url(database_path)
    engine = sqlalchemy.create_engine(url, echo=False)

    drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
    database.execute_sql_query(engine, drop_table_query)

    df_input = pd.DataFrame.from_dict({'col_1': [3], 'col_2': ['a']})
    df_input.to_sql(table_name, con=engine, if_exists='append')

    df_actual = database.load_df_from_database(engine, table_name)
    assert_frame_equal(df_input, df_actual)

    database.execute_sql_query(engine, drop_table_query)


def test_write_df_to_database():
    table_name = 'tour_data'
    user = "someUser"
    url = database.create_sqlite_url(database_path)
    engine = sqlalchemy.create_engine(url, echo=False)

    drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
    database.execute_sql_query(engine, drop_table_query)

    df_to_write = data_processing.prepare_gpx_data_for_database(gpx_path, user)
    # repeat data writing 3 x to ensure that duplicate assertion is correct
    for i in range(0, 3):
        database.write_df_to_database(df_to_write, engine, table_name)

    df_table = database.load_df_from_database(engine, table_name)

    assert len(df_to_write.index) == len(df_table.index)
