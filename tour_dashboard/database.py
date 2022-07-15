"""
Functionalities to create connection urls, load and write data to mysql or sqlite databases
"""
from typing import Dict
import logging

import sqlalchemy
import pandas as pd
from sqlalchemy.engine import Engine

from tour_dashboard import utils


# pylint: disable=C0103


def create_mysql_url(credentials: Dict[str, str]) -> str:
    """
    Create mysql connection string for authentication to database
    :param credentials: credential keys are user, password, host, port, database, table
    :return: url connection string for mysql database
    """

    user = credentials["user"]
    password = credentials["password"]
    host = credentials["host"]
    port = credentials["port"]
    database = credentials["database"]
    dialect = "mysql"
    driver = "pymysql"
    url = f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}"

    return url


def create_sqlite_engine(database_path: str) -> str:
    """
    Create sqlite connection url string
    :param database_path: local path to database
    :return: sqlite connection url string
    """

    sqlite_database_path = 'sqlite:///' + database_path

    return sqlite_database_path


def load_df_from_database(engine: Engine, table_name: str) -> pd.DataFrame:
    """
    Load all data from table to pandas DataFrame
    :param engine: database engine to connect to database
    :param table_name: table name to connect to
    :return: DataFrame with entire table data
    """
    query = f"SELECT * FROM {table_name}"
    df_table = pd.read_sql_query(query, engine)
    return df_table


def table_exists(engine: Engine, table_name: str) -> bool:
    """
    The recommended way based on docu to check for table existence
    :param engine: database engine to connect to database
    :param table_name: table name to assert
    :return: True, if table exists
    """

    return sqlalchemy.inspect(engine).has_table(table_name)


def write_df_to_database(df: pd.DataFrame, engine: Engine, table_name: str) -> None:
    """
    Write pandas DataFrame data to mysql table. Create new table if not exists. Assert whether
    tour entry based on tour_name already exists in DataFrame. If entry exists, don't write to
    table to avoid duplicates
    :param df: pandas DataFrame to write to table
    :param engine: database engine to connect to database
    :param table_name: table name to write data to
    :return: None. Will write data to database.
    """

    if not table_exists(engine, table_name):
        logging.info("Creating new table %s.", table_name)
        df.to_sql(table_name, con=engine, if_exists='append')
    else:
        # if table exists, load table and check if entry already exists
        df_table = load_df_from_database(engine, table_name)
        entry_exists = utils.entry_exists_in_table_data(df, df_table)

        if entry_exists:
            logging.info("Entry already exists. Skip writing to table: %s", table_name)
        else:
            df.to_sql(table_name, con=engine, if_exists='append')
            logging.info("New entry appended to table: %s", table_name)
