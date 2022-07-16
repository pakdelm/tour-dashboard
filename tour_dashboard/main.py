"""
Main to execute pipeline to load gpx file, process data and persist to database
"""
import logging
import sqlalchemy
import pandas as pd
from tour_dashboard import utils, data_processing, database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
pd.set_option("display.max_columns", None)


DIRECTORY = "../data"
GPX_EXTENSION = ".gpx"
DATABASE_PATH = '../data/data_concat.db'

RESOURCES = "../resources"
CREDENTIALS_PATH = f"{RESOURCES}/mysql_credentials.json"

TABLE_NAME = 'test_table_v01'
USER_NAME = "user1"

WRITE_TO_TABLE = True
PRINT_TABLE = True

if __name__ == "__main__":
    credentials = utils.parse_json(CREDENTIALS_PATH)
    mysql_url = database.create_mysql_url(credentials)
    mysql_engine = sqlalchemy.create_engine(mysql_url, echo=False)

    if WRITE_TO_TABLE:
        gpx_files = utils.create_file_paths_with_extension(DIRECTORY, GPX_EXTENSION)
        for file_path in gpx_files:
            df_to_write = data_processing.prepare_gpx_data_for_database(file_path, USER_NAME)
            database.write_df_to_database(df_to_write, mysql_engine, TABLE_NAME)

    if PRINT_TABLE:
        df_table = database.load_df_from_database(mysql_engine, TABLE_NAME)

        print(df_table.head(50))
        print(len(df_table.index))
        print(df_table.tour_name.unique())
